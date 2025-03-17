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
from dataclasses import dataclass, replace

from beartype.typing import Any, Mapping, Sequence, TypeVar, cast
from typing_extensions import Self

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.clause_params import (
    KNNSearchClauseParams,
    MetadataExtractionClauseParams,
    NLQClauseParams,
    QueryVectorClauseParams,
)
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
)
from superlinked.framework.dsl.query.param import Param, ParamInputType
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.space import Space


@dataclass(frozen=True)
class QueryClause(ABC):
    def __post_init__(self) -> None:
        self._set_param_name_if_unset()

    @property
    @abstractmethod
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]: ...

    def alter_param_values(self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool) -> Self:
        changes = self._evaluate_changes(param_values, is_override_set)
        return replace(self, **changes) if changes else self

    def get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) -> KNNSearchClauseParams:
        return knn_search_clause_params

    @abstractmethod
    def get_altered_query_vector_params(
        self,
        query_vector_params: QueryVectorClauseParams,
        index_node_id: str,
        query_schema: IdSchemaObject,
        storage_manager: StorageManager,
    ) -> QueryVectorClauseParams: ...

    def get_altered_nql_params(self, nlq_clause_params: NLQClauseParams) -> NLQClauseParams:
        return nlq_clause_params

    def get_altered_metadata_extraction_params(
        self, metadata_extraction_params: MetadataExtractionClauseParams
    ) -> MetadataExtractionClauseParams:
        return metadata_extraction_params

    def get_space_weight_param_name_by_space(self) -> dict[Space, str]:
        return {}

    def get_weight_param_name_by_space(self) -> dict[Space | None, str]:
        return dict[Space | None, str]()

    def get_default_value_by_param_name(self) -> dict[str, Any]:
        return {QueryClause.get_param(param).name: QueryClause.get_param(param).default for param in self.params}

    def get_param_value_by_param_name(self) -> dict[str, PythonTypes | None]:
        return {
            key: cast(PythonTypes | None, value)
            for param in self.params
            for key, value in QueryClause._get_value_by_param_name(param).items()
        }

    def _set_param_name_if_unset(self) -> None:
        pass

    @abstractmethod
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Any]: ...

    @staticmethod
    def get_typed_param(typed_param: TypedParam | Evaluated[TypedParam]) -> TypedParam:
        return typed_param.item if isinstance(typed_param, Evaluated) else typed_param

    @staticmethod
    def get_param(typed_param: TypedParam | Evaluated[TypedParam]) -> Param:
        return QueryClause.get_typed_param(typed_param).param

    @staticmethod
    def _get_single_param_modification(
        param: TypedParam | Evaluated[TypedParam],
        param_values: Mapping[str, ParamInputType | None],
        is_override_set: bool,
    ) -> Evaluated[TypedParam] | None:
        param_to_alter = QueryClause.get_typed_param(param)
        if (is_override_set or not isinstance(param, Evaluated)) and (
            value := param_values.get(param_to_alter.param.name)
        ) is not None:
            return param_to_alter.evaluate(value)
        return None

    @staticmethod
    def _get_param_value(param: TypedParam | Evaluated[TypedParam]) -> ParamInputType | None:
        default = QueryClause.get_param(param).default
        if isinstance(param, Evaluated):
            if param.value is None:
                return default
            return param.value
        return default

    @staticmethod
    def _get_value_by_param_name(param: TypedParam | Evaluated[TypedParam]) -> dict[str, ParamInputType | None]:
        return {QueryClause.get_param(param).name: QueryClause._get_param_value(param)}

    @staticmethod
    def _format_param_options(param: Param) -> str:
        return ", ".join(sorted(str(value) for value in param.options))

    @staticmethod
    def _to_typed_param(
        param_input: Any,
        param_types: Sequence[type],
    ) -> TypedParam | Evaluated[TypedParam]:
        param_input = cast(ParamInputType | None, param_input)
        if isinstance(param_input, Param):
            return TypedParam.from_unchecked_types(param_input, param_types)
        return TypedParam.init_evaluated(param_types, param_input)


QueryClauseT = TypeVar("QueryClauseT", bound=QueryClause)


class NLQCompatible(ABC):
    @property
    def is_type_mandatory_in_nlq(self) -> bool:
        return True

    @property
    def nlq_annotations(self) -> list[NLQAnnotation]:
        return []

    @property
    def annotation_by_space_annotation(self) -> dict[str, str]:
        return {}

    def set_defaults_for_nlq(self) -> Self:
        return self

    def get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) -> set[ParamInputType | None]:
        return QueryClause.get_param(param).options
