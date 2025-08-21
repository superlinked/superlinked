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

import asyncio
from abc import ABC, ABCMeta, abstractmethod

import structlog
from beartype.typing import Generic, Mapping, Sequence, cast

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NT, Node, NodeDataT
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage_manager.node_info import NodeInfo
from superlinked.framework.common.storage_manager.node_result_data import NodeResultData
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.dag.parent_validator import ParentValidationType
from superlinked.framework.online.online_entity_cache import OnlineEntityCache

logger = structlog.get_logger()


class OnlineNode(ABC, Generic[NT, NodeDataT], metaclass=ABCMeta):
    def __init__(
        self,
        node: NT,
        parents: Sequence[OnlineNode],
        parent_validation_type: ParentValidationType = ParentValidationType.NO_VALIDATION,
    ) -> None:
        self.node = node
        self.children: list[OnlineNode] = []
        self.parents = parents
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

    async def evaluate_next(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[NodeDataT] | None]:
        with context.dag_output_recorder.record_evaluation_exception(self.node_id):
            results = await self.evaluate_self(parsed_schemas, context, online_entity_cache)
            if self.node.persist_node_result:
                await self.persist(results, parsed_schemas, online_entity_cache)
        context.dag_output_recorder.record(self.node_id, results)
        return results

    async def evaluate_next_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> EvaluationResult[NodeDataT] | None:
        return (await self.evaluate_next([parsed_schema], context, online_entity_cache))[0]

    async def evaluate_parent(
        self,
        parent: OnlineNode,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult | None]:
        parents_results = await self.evaluate_parents([parent], parsed_schemas, context, online_entity_cache)
        return [parents_result.get(parent) for parents_result in parents_results]

    async def evaluate_parents(
        self,
        parents: Sequence[OnlineNode],
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[dict[OnlineNode, EvaluationResult]]:
        parent_evaluations = await asyncio.gather(
            *[parent.evaluate_next(parsed_schemas, context, online_entity_cache) for parent in parents]
        )
        parent_result_map = dict(zip(parents, parent_evaluations))
        results_by_schema = [
            {parent: parent_result_map[parent][schema_idx] for parent in parents}
            for schema_idx in range(len(parsed_schemas))
        ]
        return [self._validate_parents_result(schema_result) for schema_result in results_by_schema]

    def _validate_parents_result(
        self, parents_result: Mapping[OnlineNode, EvaluationResult | None]
    ) -> dict[OnlineNode, EvaluationResult]:
        parents_with_results = set(parents_result.keys())
        for non_nullable_parent in self.non_nullable_parents.intersection(parents_with_results):
            if parents_result[non_nullable_parent] is None:
                raise InvalidStateException(
                    f"{type(self).__name__} won't accept None from parent {non_nullable_parent.node_id}."
                )
        return {parent: result for parent, result in parents_result.items() if result is not None}

    @abstractmethod
    async def evaluate_self(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[NodeDataT] | None]:
        pass

    async def persist(
        self,
        results: Sequence[EvaluationResult[NodeDataT] | None],
        parsed_schemas: Sequence[ParsedSchema],
        online_entity_cache: OnlineEntityCache,
    ) -> None:
        if not parsed_schemas:
            return
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
        for node_data_item in node_data_items:
            entity_id = EntityId(schema_id=node_data_item.schema_id, object_id=node_data_item.object_id)
            if node_data_item.result is not None:
                online_entity_cache.set_node_info(
                    entity_id,
                    node_data_item.node_id,
                    NodeInfo(result=node_data_item.result),
                )
            if node_data_item.origin_id:
                online_entity_cache.set_origin(entity_id, node_data_item.origin_id)
        logger.debug(
            "stored online node data",
            schemas=lambda: {parsed_schema.schema._schema_name for parsed_schema in parsed_schemas},
            n_results=len(node_data_items),
        )

    async def load_stored_results(
        self,
        schemas_with_object_ids: Sequence[tuple[IdSchemaObject, str]],
        online_entity_cache: OnlineEntityCache,
    ) -> list[NodeDataT | None]:
        entity_ids = [
            EntityId(schema_id=schema._schema_name, object_id=object_id)
            for schema, object_id in schemas_with_object_ids
        ]
        batch_results = await online_entity_cache.get_node_results(
            entity_ids=entity_ids,
            node_id=self.node_id,
            node_data_type=self.node.node_data_type,
        )
        return [cast(NodeDataT | None, batch_results[entity_id]) for entity_id in entity_ids]

    async def load_stored_results_with_default(
        self,
        schemas_with_object_ids: Sequence[tuple[IdSchemaObject, str]],
        default_value: NodeDataT,
        online_entity_cache: OnlineEntityCache,
    ) -> list[NodeDataT]:
        return [
            default_value if result is None else result
            for result in await self.load_stored_results(schemas_with_object_ids, online_entity_cache)
        ]

    async def load_stored_results_or_raise_exception(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        online_entity_cache: OnlineEntityCache,
    ) -> list[NodeDataT]:
        schemas_with_object_ids = [(parsed_schema.schema, parsed_schema.id_) for parsed_schema in parsed_schemas]
        stored_results = await self.load_stored_results(schemas_with_object_ids, online_entity_cache)
        if none_indices := [i for i, stored_result in enumerate(stored_results) if stored_result is None]:
            wrong_parsed_schema_params = [
                f"{parsed_schemas[index].schema._schema_name}, {parsed_schemas[index].id_}" for index in none_indices
            ]
            raise InvalidStateException(
                "Node doesn't have stored values for schema, object_id pairs.",
                node_id=self.node_id,
                node_type=type(self).__name__,
                schema_object_ids=wrong_parsed_schema_params,
            )
        return cast(list[NodeDataT], stored_results)

    def validate_parents(
        self,
        parent_validation_type: ParentValidationType,
    ) -> None:
        if not parent_validation_type.validator(len(self.parents)):
            raise InvalidStateException(
                f"{type(self).__name__} must have {parent_validation_type.description}.",
                node_id=self.node_id,
                len_parents=len(self.parents),
            )
