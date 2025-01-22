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
from functools import partial

import structlog
from beartype.typing import Generic, Mapping, Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import NT, Node, NodeDataT
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
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
        results = self.evaluate_self(parsed_schemas, context)
        if self.node.persist_evaluation_result:
            for i, result in enumerate(results):
                if result is not None:
                    self.persist(result, parsed_schemas[i])
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
        inverse_parent_results = {parent: parent.evaluate_next(parsed_schemas, context) for parent in parents}
        parents_results = [
            {parent: inverse_parent_results[parent][i] for parent in parents} for i in range(len(parsed_schemas))
        ]
        return [self._validate_parents_result(parents_result) for parents_result in parents_results]

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
        result: EvaluationResult[NodeDataT],
        parsed_schema: ParsedSchema,
    ) -> None:
        self.storage_manager.write_node_result(
            parsed_schema.schema,
            parsed_schema.id_,
            result.main.node_id,
            result.main.value,
        )
        for chunk in result.chunks:
            self.storage_manager.write_node_result(
                parsed_schema.schema,
                chunk.object_id,
                chunk.node_id,
                chunk.value,
                parsed_schema.id_,
            )
        logger.debug(
            "stored online node data",
            schema=parsed_schema.schema._schema_name,
            pii_main_result=partial(str, result.main.value),
            pii_chunk_result=lambda: [str(chunk.value) for chunk in result.chunks],
        )

    def load_stored_results(
        self, schemas_with_object_ids: Sequence[tuple[SchemaObject, str]]
    ) -> list[NodeDataT | None]:
        return self.storage_manager.read_node_results(
            schemas_with_object_ids,
            self.node_id,
            self.node.node_data_type,
        )

    def load_stored_results_with_default(
        self, schemas_with_object_ids: Sequence[tuple[SchemaObject, str]], default_value: NodeDataT
    ) -> list[NodeDataT]:
        return [
            default_value if result is None else result for result in self.load_stored_results(schemas_with_object_ids)
        ]

    def load_stored_result(self, schema: SchemaObject, object_id: str) -> NodeDataT | None:
        return self.load_stored_results([(schema, object_id)])[0]

    def load_stored_result_or_raise_exception(
        self,
        parsed_schema: ParsedSchema,
    ) -> NodeDataT:
        stored_result = self.load_stored_result(parsed_schema.schema, parsed_schema.id_)
        if stored_result is None:
            raise DagEvaluationException(
                f"{self.node_id} doesn't have a stored value for (schema, object_id):"
                + f" ({parsed_schema.schema._schema_name}, {parsed_schema.id_})"
            )
        return stored_result

    def validate_parents(
        self,
        parent_validation_type: ParentValidationType,
    ) -> None:
        if not parent_validation_type.validator(len(self.parents)):
            raise ParentCountException(f"{type(self).__name__} must have {parent_validation_type.description}.")
