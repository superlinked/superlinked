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


from abc import ABC, abstractmethod
from dataclasses import dataclass

from beartype.typing import Any, Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.clause_params import QueryVectorClauseParams
from superlinked.framework.dsl.query.param import UNSET_PARAM_NAME, ParamInputType
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.typed_param import TypedParam

VALUE_PARAM_FIELD = "value_param"


@dataclass(frozen=True)
class SingleValueParamQueryClause(QueryClause, ABC):
    value_param: TypedParam | Evaluated[TypedParam]

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [self.value_param]

    @override
    async def get_altered_query_vector_params(
        self,
        query_vector_params: QueryVectorClauseParams,
        index_node_id: str,
        query_schema: IdSchemaObject,
        storage_manager: StorageManager,
    ) -> QueryVectorClauseParams:
        return query_vector_params

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        param = QueryClause.get_param(self.value_param)
        if param.name is UNSET_PARAM_NAME:
            param.name = self._get_default_value_param_name()

    def _get_value(self) -> PythonTypes | None:
        value = QueryClause._get_param_value(self.value_param)
        return cast(PythonTypes | None, value)

    @override
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Any]:
        if modified_param := QueryClause._get_single_param_modification(
            self.value_param, param_values, is_override_set
        ):
            return {VALUE_PARAM_FIELD: modified_param}
        return {}

    @abstractmethod
    def _get_default_value_param_name(self) -> str: ...
