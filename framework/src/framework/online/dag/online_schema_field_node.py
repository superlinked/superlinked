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

from beartype.typing import Generic, Sequence
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SFT
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType
from superlinked.framework.online.online_entity_cache import OnlineEntityCache


class OnlineSchemaFieldNode(Generic[SFT], OnlineNode[SchemaFieldNode, SFT]):
    def __init__(
        self,
        node: SchemaFieldNode,
        parents: list[OnlineNode],
    ) -> None:
        super().__init__(node, parents, ParentValidationType.NO_PARENTS)

    @override
    async def evaluate_self(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[SFT] | None]:
        parsed_schema_values = [self._get_parsed_schema_value(parsed_schema) for parsed_schema in parsed_schemas]
        stored_results = await self._calculate_stored_result_by_id(
            parsed_schemas, parsed_schema_values, online_entity_cache
        )
        return [
            self._to_result(stored_results.get(parsed_schema.id_) if value is None else value)
            for parsed_schema, value in zip(parsed_schemas, parsed_schema_values)
        ]

    async def _calculate_stored_result_by_id(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        parsed_schema_values: Sequence[SFT | None],
        online_entity_cache: OnlineEntityCache,
    ) -> dict[str, SFT | None]:
        parsed_schema_ids_without_value = set(
            parsed_schema.id_ for parsed_schema, value in zip(parsed_schemas, parsed_schema_values) if not value
        )
        if not self.node.persist_node_result or not parsed_schema_ids_without_value:
            return {}

        schemas_with_object_ids = [
            (self.node.schema_field.schema_obj, parsed_schema_id)
            for parsed_schema_id in parsed_schema_ids_without_value
        ]
        return dict(
            zip(
                parsed_schema_ids_without_value,
                await self.load_stored_results(schemas_with_object_ids, online_entity_cache),
            )
        )

    def _get_parsed_schema_value(self, parsed_schema: ParsedSchema) -> SFT | None:
        return next(
            (field.value for field in parsed_schema.fields if field.schema_field == self.node.schema_field), None
        )

    def _to_result(self, value: SFT | None) -> EvaluationResult[SFT] | None:
        if value is not None:
            return EvaluationResult(self._get_single_evaluation_result(value))
        if self.node.schema_field.nullable:
            return None
        field_name = f"{self.node.schema_field.schema_obj._schema_name}.{self.node.schema_field.name}"
        raise InvalidInputException(
            (
                f"The SchemaField {field_name} was not supplied in the input data. "
                "If you want to ingest missing data for this field, make it optional."
            )
        )
