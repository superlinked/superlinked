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


from beartype.typing import Any, Sequence, Union
from pydantic import BaseModel, Field, create_model

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler.query_param_model_validator import (
    QueryParamModelValidator,
)
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.typed_param import TypedParam

QUERY_MODEL_NAME = "QueryModel"
VALIDATORS_ARG_NAME = "__validators__"
VALIDATOR_NAME = "__validator__"
VALID_NLQ_TYPES = frozenset([float, int, str, list[float], list[int], list[str]])

_FieldSpecification = tuple[Any, Any]  # (type, field)
_ParamType = TypedParam | Evaluated[TypedParam]


class QueryParamModelBuilder:

    @classmethod
    def build(cls, clause_collector: NLQClauseCollector) -> type[BaseModel]:
        field_kwargs: dict[str, Any] = cls._calculate_field_kwargs(clause_collector)
        validation_kwargs = {VALIDATORS_ARG_NAME: {VALIDATOR_NAME: QueryParamModelValidator.build(clause_collector)}}
        pydantic_kwargs = field_kwargs | validation_kwargs
        model = create_model(QUERY_MODEL_NAME, **pydantic_kwargs)
        return model

    @classmethod
    def _calculate_field_kwargs(cls, clause_collector: NLQClauseCollector) -> dict[str, _FieldSpecification]:
        weight_param_names = clause_collector.space_weight_param_info.get_weight_param_names()
        field_specs = {}

        for clause_handler in clause_collector.clause_handlers:
            for param in clause_handler.clause.params:
                param_name = QueryClause.get_param(param).name
                is_weight_param = param_name in weight_param_names
                field_specs[param_name] = cls._create_field_specification(
                    param, clause_handler.is_type_mandatory_in_nlq, is_weight_param
                )

        return field_specs

    @classmethod
    def _create_field_specification(
        cls, param: _ParamType, is_type_mandatory: bool, is_weight_param: bool
    ) -> _FieldSpecification:
        param_type = cls._determine_param_type(param, is_type_mandatory, is_weight_param)
        field_instance = cls._create_field_instance(param)
        return (param_type, field_instance)

    @classmethod
    def _determine_param_type(cls, param: _ParamType, is_type_mandatory: bool, is_weight_param: bool) -> Any:
        if is_weight_param:
            return constants.NLQ_WEIGHT_TYPE
        supported_types = cls._extract_supported_nlq_types(param)
        unified_type = cls._merge_types(supported_types)
        return unified_type if is_type_mandatory else unified_type | None

    @classmethod
    def _extract_supported_nlq_types(cls, param: _ParamType) -> list[type]:
        typed_param = QueryClause.get_typed_param(param)
        param_types = typed_param.valid_param_value_types
        supported_types = [
            param_type.original_type for param_type in param_types if param_type.original_type in VALID_NLQ_TYPES
        ]
        if not supported_types:
            param_name = QueryClause.get_param(param).name
            raise InvalidInputException(f"No NLQ-supported type found for parameter: {param_name}")
        return supported_types

    @classmethod
    def _merge_types(cls, types_list: Sequence[type]) -> Any:
        if len(types_list) == 1:
            return types_list[0]
        return Union[tuple(types_list)]

    @classmethod
    def _create_field_instance(cls, param: _ParamType) -> Any:
        match param:
            case Evaluated():
                return param.value
            case _ if (default_value := QueryClause.get_param(param).default) is not None:
                return Field(default=default_value)
            case _:
                return Field()
