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


from beartype.typing import Any, Union
from pydantic import BaseModel, Field, create_model

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

VALID_NLQ_TYPES = [float, int, str, list[float], list[int], list[str]]


class QueryParamModelBuilder:
    @classmethod
    def build(cls, clause_collector: NLQClauseCollector) -> type[BaseModel]:
        field_kwargs: dict[str, Any] = cls._calculate_field_kwargs(clause_collector)
        validation_kwargs = {VALIDATORS_ARG_NAME: {VALIDATOR_NAME: QueryParamModelValidator.build(clause_collector)}}
        pydantic_kwargs = field_kwargs | validation_kwargs
        model = create_model(QUERY_MODEL_NAME, **pydantic_kwargs)
        return model

    @classmethod
    def _calculate_field_kwargs(cls, clause_collector: NLQClauseCollector) -> dict[str, tuple[Any, Any]]:
        return {
            QueryClause.get_param(param).name: (
                cls._calculate_type(param, clause_handler.is_type_mandatory_in_nlq),
                cls._calculate_field(param),
            )
            for clause_handler in clause_collector.clause_handlers
            for param in clause_handler.clause.params
        }

    @classmethod
    def _calculate_type(cls, param: TypedParam | Evaluated[TypedParam], is_type_mandatory: bool) -> Any:
        param_types = QueryClause.get_typed_param(param).valid_param_value_types
        nlq_types = [
            param_type.original_type for param_type in param_types if param_type.original_type in VALID_NLQ_TYPES
        ]
        if not nlq_types:
            raise InvalidInputException(
                f"No NLQ-supported type found for parameter: {QueryClause.get_param(param).name}"
            )
        types = Union[tuple(nlq_types)] if len(nlq_types) > 1 else nlq_types[0]
        return types if is_type_mandatory else types | None

    @classmethod
    def _calculate_field(cls, param: TypedParam | Evaluated[TypedParam]) -> Any:
        match param:
            case Evaluated():
                return param.value
            case _ if (default_value := QueryClause.get_param(param).default) is not None:
                return Field(default=default_value)
            case _:
                return Field()
