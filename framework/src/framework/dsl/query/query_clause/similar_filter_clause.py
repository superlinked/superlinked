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

from collections import defaultdict
from dataclasses import dataclass

from beartype.typing import Any, Mapping, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.const import constants
from superlinked.framework.common.data_types import NodeDataTypes, PythonTypes
from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.interface.weighted import Weighted
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import Blob
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.dsl.query.clause_params import QueryVectorClauseParams
from superlinked.framework.dsl.query.param import (
    UNSET_PARAM_NAME,
    NumericParamType,
    ParamInputType,
    ParamType,
)
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)
from superlinked.framework.dsl.query.typed_param import TypedParam
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet
from superlinked.framework.query.query_node_input import (
    QueryNodeInput,
    QueryNodeInputValue,
)

WEIGHT_PARAM_FIELD = "weight_param"


@dataclass(frozen=True)
class SimilarFilterClause(SingleValueParamQueryClause, NLQCompatible):
    weight_param: TypedParam | Evaluated[TypedParam]
    field_set: SpaceFieldSet

    @property
    @override
    def params(self) -> Sequence[TypedParam | Evaluated[TypedParam]]:
        return [*super().params, self.weight_param]

    @property
    @override
    def annotation_by_space_annotation(self) -> dict[str, str]:
        if any(isinstance(field, Blob) for field in self.field_set.fields):
            return {}
        return {self.field_set.space.annotation: self.__get_annotation()}

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
        _, weighted_value = result
        node_id = self.field_set.space._get_embedding_node(query_schema).node_id
        node_input = QueryNodeInput(
            QueryNodeInputValue(
                cast(NodeDataTypes, await self.field_set._generate_space_input(weighted_value.item)),
                weighted_value.weight,
            ),
            False,
        )
        query_node_inputs_by_node_id[node_id].append(node_input)
        return query_vector_params.set_params(query_node_inputs_by_node_id=dict(query_node_inputs_by_node_id))

    @override
    def get_weight_param_name_by_space(self) -> dict[Space | None, str]:
        return super().get_weight_param_name_by_space() | {
            self.field_set.space: QueryClause.get_param(self.weight_param).name
        }

    @override
    def get_default_value_by_param_name(self) -> dict[str, Any]:
        def get_default_weight(weight: TypedParam | Evaluated[TypedParam]) -> Any:
            default = QueryClause.get_param(weight).default
            if default is None:
                return constants.DEFAULT_WEIGHT
            return default

        defaults = super().get_default_value_by_param_name()
        return defaults | {QueryClause.get_param(self.weight_param).name: get_default_weight(self.weight_param)}

    @override
    def get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) -> set[ParamInputType | None]:
        if param == self.weight_param:
            return super().get_allowed_values(self.weight_param)
        categories: set[ParamInputType | None] = (
            set(self.field_set.space._embedding_config.categories)
            if isinstance(self.field_set.space, CategoricalSimilaritySpace)
            else set()
        )
        options = QueryClause.get_param(param).options
        if options and not categories:
            return options
        if categories and not options:
            return categories
        return options.intersection(categories)

    @override
    def _get_default_value_param_name(self) -> str:
        return f"similar_filter_{self.field_set.space}_{self.field_set.fields_id}_value_param__"

    @override
    def _evaluate_changes(
        self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool
    ) -> dict[str, Evaluated[TypedParam]]:
        changes = super()._evaluate_changes(param_values, is_override_set)
        if modified_param := QueryClause._get_single_param_modification(
            self.weight_param, param_values, is_override_set
        ):
            return changes | {WEIGHT_PARAM_FIELD: modified_param}
        return changes

    @override
    def _set_param_name_if_unset(self) -> None:
        super()._set_param_name_if_unset()
        weight_param = QueryClause.get_param(self.weight_param)
        if weight_param.name is UNSET_PARAM_NAME:
            weight_param.name = self.__get_default_weight_param_name()

    def _get_weight(self) -> float:
        weight = QueryClause._get_param_value(self.weight_param)
        if weight is None:
            return constants.DEFAULT_WEIGHT
        if not isinstance(weight, (int, float)):
            raise InvalidInputException(f"Clause weight should be numeric, got {type(weight).__name__}.")
        return float(weight)

    def __get_default_weight_param_name(self) -> str:
        return f"similar_filter_{self.field_set.space}_{self.field_set.fields_id}_weight_param__"

    def __get_annotation(self) -> str:
        value_param = QueryClause.get_param(self.value_param)
        value_accepted_type = self.field_set.input_type
        weight_param = QueryClause.get_param(self.weight_param)
        v_options = QueryClause._format_param_options(value_param)
        w_options = QueryClause._format_param_options(weight_param)
        v_description = value_param.description or ""
        w_description = weight_param.description or ""
        return "".join(
            (
                f"  - {value_param.name}: A {value_accepted_type.__name__} " "representing a similarity-search item.",
                f"\n    - **Possible values:** {v_options}." if v_options else "",
                f"\n    - **Description:** {v_description}" if v_description else "",
                "\n    - **Usage:** Encoded into a vector, used to find similar items, "
                "and combined with others based on weights.",
                f"\n  - {weight_param.name}: A {float.__name__} "
                "controlling the importance of this similarity-search item within the same space.",
                (f"\n    - **Possible values:** {w_options}." if w_options else ""),
                f"\n    - **Description:** {w_description}" if w_description else "",
                "\n    - **Usage:** Same as `space_weight`, but within the space",
            )
        )

    def __evaluate(
        self,
    ) -> tuple[Space, Weighted[PythonTypes]] | None:
        value = self._get_value()
        weight = self._get_weight()
        if value is None or weight == constants.DEFAULT_NOT_AFFECTING_WEIGHT:
            return None
        return (self.field_set.space, Weighted(value, weight))

    @classmethod
    def from_param(
        cls, spaces: Sequence[Space], field_set: SpaceFieldSet, param: ParamType, weight: NumericParamType
    ) -> SimilarFilterClause:
        SimilarFilterClause.__validate_spaces(field_set, spaces)
        value_param = QueryClause._to_typed_param(param, field_set.validated_allowed_param_types)
        weight_param = QueryClause._to_typed_param(weight, [float])
        return SimilarFilterClause(value_param, weight_param, field_set)

    @classmethod
    def __validate_spaces(cls, field_set: SpaceFieldSet, spaces: Sequence[Space]) -> None:
        if not field_set.space.allow_similar_clause:
            raise InvalidInputException(
                f"Similar clause is not possible for {type(field_set.space).__name__}"
                " as the space configuration implies it."
            )
        if field_set.space not in spaces:
            raise InvalidInputException(f"Space isn't present in the index: {type(field_set.space).__name__}.")
