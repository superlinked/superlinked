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

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass

from beartype.typing import Any, cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.data_types import NodeDataTypes, Vector
from superlinked.framework.common.exception import (
    InvalidInputException,
    NotFoundException,
)
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.telemetry.telemetry_registry import telemetry
from superlinked.framework.dsl.query.clause_params import QueryVectorClauseParams
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.query.query_node_input import (
    QueryNodeInput,
    QueryNodeInputValue,
)


@dataclass(frozen=True)
class BaseLooksLikeFilterClause(NLQCompatible, SingleValueParamQueryClause, ABC):
    schema_field: IdField

    def __post_init__(self) -> None:
        super().__post_init__()
        BaseLooksLikeFilterClause._validate_schema_object(self.schema_field)

    @override
    async def get_altered_query_vector_params(
        self,
        query_vector_params: QueryVectorClauseParams,
        index_node_id: str,
        query_schema: IdSchemaObject,
        storage_manager: StorageManager,
    ) -> QueryVectorClauseParams:
        result = self.__evaluate()
        if not result:
            return query_vector_params
        query_node_inputs_by_node_id = defaultdict[str, list[QueryNodeInput]](
            list, query_vector_params.query_node_inputs_by_node_id
        )
        object_id, weight = result
        vector = await self.__get_looks_like_vector(
            index_node_id, self.schema_field.schema_obj, object_id, storage_manager
        )
        node_input = QueryNodeInput(
            QueryNodeInputValue(cast(NodeDataTypes, vector), weight),
            True,
        )
        query_node_inputs_by_node_id[index_node_id].append(node_input)
        return query_vector_params.set_params(query_node_inputs_by_node_id=dict(query_node_inputs_by_node_id))

    @override
    def _get_default_value_param_name(self) -> str:
        return f"with_vector_{self.schema_field.name}_value_param__"

    def _is_weight_unaffecting(self, weight: float | dict[str, float]) -> bool:
        if isinstance(weight, dict):
            return all(space_weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT for space_weight in weight.values())
        return isinstance(weight, float) and weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT

    @abstractmethod
    def _get_weight(self) -> float | dict[str, float]: ...

    @staticmethod
    def _get_default_weight(weight: TypedParam | Evaluated[TypedParam]) -> Any:
        default = QueryClause.get_param(weight).default
        if default is None:
            return constants.DEFAULT_WEIGHT
        return default

    def __evaluate(self) -> tuple[str, float | dict[str, float]] | None:
        value = self._get_value()
        weight = self._get_weight()
        if value is None or self._is_weight_unaffecting(weight):
            return None
        return cast(str, value), weight

    async def __get_looks_like_vector(
        self, index_node_id: str, schema_obj: IdSchemaObject, object_id: str, storage_manager: StorageManager
    ) -> Vector:
        with telemetry.span(
            "storage.read.node.result",
            attributes={
                "schema": schema_obj._schema_name,
                "object_id": object_id,
                "node_id": index_node_id,
                "data_type": Vector.__name__,
            },
        ):
            vector: Vector | None = await storage_manager.read_node_result(schema_obj, object_id, index_node_id, Vector)
        if vector is None:
            raise NotFoundException(f"Entity not found for object_id: {object_id} node_id: {index_node_id}")
        return vector

    @classmethod
    def _validate_schema_object(cls, id_: IdField) -> None:
        if not isinstance(id_.schema_obj, IdSchemaObject):
            raise InvalidInputException(f"'with_vector': {type(id_.schema_obj).__name__} is not a schema.")
