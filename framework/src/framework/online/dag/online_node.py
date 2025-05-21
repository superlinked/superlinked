# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

import structlog
from beartype.typing import Generic, Mapping, Sequence, cast

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import NT, Node, NodeDataT
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.node_result_data import NodeResultData
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.dag.exception import ParentResultException
from superlinked.framework.online.dag.parent_validator import ParentValidationType

logger = structlog.get_logger()


class OnlineNode(ABC, Generic[NT, NodeDataT], metaclass=ABCMeta):
    def __init__(
        self,
        node: NT,
        parents: Sequence[OnlineNode],
        storage_manager: StorageManager,
        parent_validation_type: ParentValidationType = ParentValidationType.NO_VALIDATION,
    ) -> None:
        self.node = node
        self.children: list[OnlineNode] = []
        self.parents = parents
        self.storage_manager = storage_manager
        self.validate_parents(parent_validation_type)
        for parent in self.parents:
            parent.children.append(self)
        self.non_nullable_parents = self._init_non_nullable_parents(node, parents)

    @property
    def class_name(self) -> str:
        return type(self).__name__

    @property
    def node_id(self) -> str:
        return self.node.node_id

    def _init_non_nullable_parents(self, node: Node, parents: Sequence[OnlineNode]) -> frozenset[OnlineNode]:
        non_nullable_parent_ids = [non_nullable_parent.node_id for non_nullable_parent in node.non_nullable_parents]
        return frozenset([parent for parent in parents if parent.node_id in non_nullable_parent_ids])

    def _get_single_evaluation_result(self, value: NodeDataT) -> SingleEvaluationResult[NodeDataT]:
        return SingleEvaluationResult(self.node_id, value)

    def _wrap_in_evaluation_result(
        self, result: NodeDataT, chunks: Sequence[NodeDataT] | None = None
    ) -> EvaluationResult[NodeDataT]:
        return EvaluationResult(
            self._get_single_evaluation_result(result),
            [self._get_single_evaluation_result(chunk) for chunk in (chunks or [])],
        )

    def evaluate_next(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[NodeDataT] | None]:
        with context.dag_output_recorder.record_evaluation_exception(self.node_id):
            results = self.evaluate_self(parsed_schemas, context)
            if self.node.persist_node_result:
                self.persist(results, parsed_schemas)
        context.dag_output_recorder.record(self.node_id, results)
        return results

    def evaluate_next_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[NodeDataT] | None:
        return self.evaluate_next([parsed_schema], context)[0]

    def evaluate_parent(
        self, parent: OnlineNode, parsed_schemas: Sequence[ParsedSchema], context: ExecutionContext
    ) -> list[EvaluationResult | None]:
        parents_results = self.evaluate_parents([parent], parsed_schemas, context)
        return [parents_result.get(parent) for parents_result in parents_results]

    def evaluate_parents(
        self, parents: Sequence[OnlineNode], parsed_schemas: Sequence[ParsedSchema], context: ExecutionContext
    ) -> list[dict[OnlineNode, EvaluationResult]]:
        inverse_parent_results = self._evaluate_parents_concurrently(parents, parsed_schemas, context)
        parents_results = [
            {parent: inverse_parent_results[parent][i] for parent in parents} for i in range(len(parsed_schemas))
        ]
        return [self._validate_parents_result(parents_result) for parents_result in parents_results]

    def _evaluate_parents_concurrently(
        self, parents: Sequence[OnlineNode], parsed_schemas: Sequence[ParsedSchema], context: ExecutionContext
    ) -> dict[OnlineNode, list[EvaluationResult | None]]:
        parent_results = {parent: parent.evaluate_next(parsed_schemas, context) for parent in parents}
        return parent_results

    def _validate_parents_result(
        self, parents_result: Mapping[OnlineNode, EvaluationResult | None]
    ) -> dict[OnlineNode, EvaluationResult]:
        parents_with_results = set(parents_result.keys())
        for non_nullable_parent in self.non_nullable_parents.intersection(parents_with_results):
            if parents_result[non_nullable_parent] is None:
                raise ParentResultException(
                    f"{type(self).__name__} won't accept None from parent {non_nullable_parent.node_id}."
                )
        return {parent: result for parent, result in parents_result.items() if result is not None}

    @abstractmethod
    def evaluate_self(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[NodeDataT] | None]:
        pass

    def persist(
        self,
        results: Sequence[EvaluationResult[NodeDataT] | None],
        parsed_schemas: Sequence[ParsedSchema],
    ) -> None:
        node_data_items = [
            data
            for i, result in enumerate(results)
            if result is not None
            for data in [
                NodeResultData(
                    parsed_schemas[i].schema._schema_name, parsed_schemas[i].id_, result.main.node_id, result.main.value
                ),
                *[
                    NodeResultData(
                        parsed_schemas[i].schema._schema_name,
                        chunk.object_id,
                        chunk.node_id,
                        chunk.value,
                        parsed_schemas[i].id_,
                    )
                    for chunk in result.chunks
                ],
            ]
        ]
        self.storage_manager.write_node_results(node_data_items)
        logger.debug(
            "stored online node data",
            schemas=lambda: {parsed_schema.schema._schema_name for parsed_schema in parsed_schemas},
            n_results=len(node_data_items),
        )

    def load_stored_results(
        self, schemas_with_object_ids: Sequence[tuple[SchemaObject, str]]
    ) -> list[NodeDataT | None]:
        if not schemas_with_object_ids:
            return []
        distinct_keys = list(set(schemas_with_object_ids))
        distinct_stored_results = self.storage_manager.read_node_results(
            distinct_keys,
            self.node_id,
            self.node.node_data_type,
        )
        distinct_stored_result_by_key = dict(zip(distinct_keys, distinct_stored_results))
        return [distinct_stored_result_by_key[key] for key in schemas_with_object_ids]

    def load_stored_results_with_default(
        self, schemas_with_object_ids: Sequence[tuple[SchemaObject, str]], default_value: NodeDataT
    ) -> list[NodeDataT]:
        return [
            default_value if result is None else result for result in self.load_stored_results(schemas_with_object_ids)
        ]

    def load_stored_results_or_raise_exception(
        self,
        parsed_schemas: Sequence[ParsedSchema],
    ) -> list[NodeDataT]:
        schemas_with_object_ids = [(parsed_schema.schema, parsed_schema.id_) for parsed_schema in parsed_schemas]
        stored_results = self.load_stored_results(schemas_with_object_ids)
        if none_indices := [i for i, stored_result in enumerate(stored_results) if stored_result is None]:
            wrong_parsed_schema_params = [
                f"{parsed_schemas[index].schema._schema_name}, {parsed_schemas[index].id_}" for index in none_indices
            ]
            raise DagEvaluationException(
                f"{self.node_id} doesn't have stored values for the following (schema, object_id) pairs:"
                + f" ({wrong_parsed_schema_params})"
            )
        return cast(list[NodeDataT], stored_results)

    def validate_parents(
        self,
        parent_validation_type: ParentValidationType,
    ) -> None:
        if not parent_validation_type.validator(len(self.parents)):
            raise ParentCountException(
                f"{type(self).__name__} must have {parent_validation_type.description}, got {len(self.parents)}"
            )
