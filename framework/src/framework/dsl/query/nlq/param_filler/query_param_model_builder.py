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


from beartype.typing import Any, Optional
from pydantic import BaseModel, Field, create_model

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.nlq.param_filler.query_param_model_validator import (
    QueryParamModelValidator,
)
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query_clause import (
    HardFilterClause,
    QueryClause,
    WeightedQueryClause,
)

QUERY_MODEL_NAME = "QueryModel"
VALIDATORS_ARG_NAME = "__validators__"
VALIDATOR_NAME = "__validator__"


class QueryParamModelBuilder:

    @classmethod
    def build(cls, clause_collector: NLQClauseCollector) -> type[BaseModel]:
        field_kwargs: dict[str, Any] = cls._calculate_field_kwargs(clause_collector)
        validation_kwargs = {VALIDATORS_ARG_NAME: {VALIDATOR_NAME: QueryParamModelValidator.build(clause_collector)}}
        pydantic_kwargs = {**field_kwargs, **validation_kwargs}
        model = create_model(QUERY_MODEL_NAME, **pydantic_kwargs)
        return model

    @classmethod
    def _calculate_field_kwargs(cls, clause_collector: NLQClauseCollector) -> dict[str, tuple[Any, Any]]:
        return {
            query_clause.get_param(param).name: (
                cls._calculate_type(query_clause, param),
                cls._calculate_field(query_clause, param),
            )
            for query_clause in clause_collector.clauses
            for param in query_clause.params
        }

    @classmethod
    def _calculate_type(cls, query_clause: QueryClause, param: Param | Evaluated[Param]) -> Any:
        if isinstance(query_clause, WeightedQueryClause) and query_clause.weight_param == param:
            return query_clause.weight_accepted_type
        if isinstance(query_clause, HardFilterClause):
            return Optional[query_clause.value_accepted_type]
        return query_clause.value_accepted_type

    @classmethod
    def _calculate_field(cls, query_clause: QueryClause, param: Param | Evaluated[Param]) -> Any:
        match param:
            case Evaluated():
                return param.value
            case _ if (default_value := query_clause.get_param(param).default):
                return Field(default=default_value)
            case _:
                return Field()
