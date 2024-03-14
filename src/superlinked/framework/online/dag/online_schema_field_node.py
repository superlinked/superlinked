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

from typing import Generic, cast

from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.schema_object import SFT, Timestamp
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.exception import ValueNotProvidedException
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineSchemaFieldNode(Generic[SFT], OnlineNode[SchemaFieldNode, SFT]):
    def __init__(
        self,
        node: SchemaFieldNode,
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(node, [], evaluation_result_store_manager)

    @classmethod
    def from_node(
        cls,
        node: SchemaFieldNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> OnlineSchemaFieldNode:
        if len(parents) != 0:
            raise InitializationException(f"{cls.__name__} cannot have parents.")
        return cls(node, evaluation_result_store_manager)

    @classmethod
    def get_node_type(cls) -> type[SchemaFieldNode]:
        return SchemaFieldNode

    @override
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[SFT]:
        parsed_nodes: list[ParsedSchemaField] = [
            field
            for field in parsed_schema.fields
            if field.schema_field == self.node.schema_field
        ]
        result: SFT
        if parsed_nodes:
            result = parsed_nodes[0].value
        else:
            result = self.__get_default_result(parsed_schema, context)
        return EvaluationResult(self._get_single_evaluation_result(result))

    def __get_default_result(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> SFT:
        stored_result = self.load_stored_result(parsed_schema.id_, parsed_schema.schema)
        if stored_result:
            return stored_result
        if isinstance(self.node.schema_field, Timestamp):
            return cast(SFT, context.now())
        field_name = ".".join(
            [
                self.node.schema_field.schema_obj._schema_name,
                self.node.schema_field.name,
            ]
        )
        raise ValueNotProvidedException(
            (
                f"The SchemaField {field_name} "
                + "doesn't have a default value and was not provided in the ParsedSchema.",
            )
        )
