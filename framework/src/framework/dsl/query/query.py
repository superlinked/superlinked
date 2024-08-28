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

from beartype.typing import NamedTuple, cast
from typing_extensions import Annotated

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import (
    InvalidSchemaException,
    QueryException,
)
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
    _Or,
)
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema import T
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import (
    IntParamType,
    NumericParamType,
    ParamInputType,
    ParamType,
    StringParamType,
)
from superlinked.framework.dsl.query.query_filter_information import (
    HardFilterInformation,
    LooksLikeFilterInformation,
    QueryFilterInformation,
    SimilarFilterInformation,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.query.query_param_information import (
    ParamGroup,
    ParamInfo,
    QueryParamInformation,
    WeightedParamInfo,
)
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["AlterParams"] = False


class AlterParams(NamedTuple):
    space_weight_params: list[ParamInfo] | None = None
    hard_filter_params: list[ParamInfo] | None = None
    similar_filter_params: list[WeightedParamInfo] | None = None
    looks_like_filter_param: WeightedParamInfo | None = None
    limit_param: ParamInfo | None = None
    radius_param: ParamInfo | None = None
    natural_query_param: ParamInfo | None = None
    hard_filter_infos: list[HardFilterInformation] | None = None
    similar_filter_infos: list[SimilarFilterInformation] | None = None
    looks_like_filter_info: LooksLikeFilterInformation | None = None
    natural_query_client_config: OpenAIClientConfig | None = None
    override_now: int | None = None


@TypeValidator.wrap
class QueryObj:  # pylint: disable=too-many-instance-attributes
    """
    A class representing a query object. Use .with_vector to run queries using a stored
    vector, or use .similar for queries where you supply the query at query-time. Or combine
    them, or even combine multiple .similar to supply different queries for each space in the
    Index.

    Attributes:
        builder (Query): The query builder.
        schema (SchemaObject): The schema object.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        index: Index,
        schema: IdSchemaObject,
        query_param_info: QueryParamInformation | None = None,
        query_filter_info: QueryFilterInformation | None = None,
        override_now: int | None = None,
        natural_query_client_config: OpenAIClientConfig | None = None,
    ) -> None:
        """
        Initialize the QueryObj.

        Args:
            builder (Query): The query builder.
            schema (IdSchemaObject): The schema object.
        """
        self.index = index
        self.schema = schema
        self._override_now = override_now
        self.natural_query_client_config = natural_query_client_config
        self.query_param_info = query_param_info or QueryParamInformation()
        self.query_filter_info = query_filter_info or QueryFilterInformation()

    def override_now(self, now: int) -> QueryObj:
        return self.__alter(AlterParams(override_now=now))

    def similar(
        self,
        field_set: SpaceFieldSet,
        param: ParamType,
        weight: NumericParamType = constants.DEFAULT_WEIGHT,
    ) -> QueryObj:
        """
        Add a 'similar' clause to the query. Similar queries compile query inputs (like query text) into vectors
        using a space and then use the query_vector (weighted with weight param) to search
        in the referenced space of the index.

        Args:
            field_set (SpaceFieldSet): The referenced space.
            param (ParamType): The parameter. Basically the query itself. It can be a fixed value,
            or a placeholder (Param) for later substitution.
            weight (NumericParamType, optional): The weight. Defaults to 1.0.

        Returns:
            Self: The query object itself.

        Raises:
            QueryException: If the space is already bound in the query.
            InvalidSchemaException: If the schema is not in the similarity field's schema types.
        """
        if not self.__is_indexed_space(field_set.space):
            raise QueryException("Space isn't present in the index.")

        if self.__is_space_bound(field_set.space):
            raise QueryException("Space attempted to bound in query multiple times.")

        relevant_field = field_set.get_field_for_schema(self.schema)
        if not relevant_field:
            raise InvalidSchemaException(
                f"'find' ({type(self.schema)}) is not in similarity field's schema types."
            )
        similar_filter_param = WeightedParamInfo.init_with(
            ParamGroup.SIMILAR_FILTER_VALUE,
            ParamGroup.SIMILAR_FILTER_WEIGHT,
            param,
            weight,
            relevant_field,
            field_set.space,
        )
        similar_filter_information = SimilarFilterInformation(
            field_set.space,
            relevant_field,
            similar_filter_param.value_param.name,
        )
        return self.__alter(
            AlterParams(
                similar_filter_params=self.query_param_info.similar_filter_params
                + [similar_filter_param],
                similar_filter_infos=self.query_filter_info.similar_filter_infos
                + [similar_filter_information],
            )
        )

    def limit(self, limit: IntParamType | None) -> QueryObj:
        """
        Set a limit to the number of results returned by the query.
        If the limit is None, -1 will be used, which is not handled by all databases.

        Args:
            limit (IntParamType): The maximum number of results to return.
        Returns:
            Self: The query object itself.
        """
        limit_param = ParamInfo.init_with(ParamGroup.LIMIT, limit)
        return self.__alter(AlterParams(limit_param=limit_param))

    def with_natural_query(
        self, natural_query: StringParamType, client_config: OpenAIClientConfig
    ) -> QueryObj:
        """
        Sets a natural language query based on which empty Params will have values set.

        Args:
            natural_query (StringParamType): Query containing desired characteristics.
            client_config (OpenAIClientConfig): Client config to initialize the client with.
        Returns:
            Self: The query object itself.
        """
        natural_query_param = ParamInfo.init_with(
            ParamGroup.NATURAL_QUERY, natural_query
        )
        return self.__alter(
            AlterParams(
                natural_query_param=natural_query_param,
                natural_query_client_config=client_config,
            )
        )

    def radius(self, radius: NumericParamType | None) -> QueryObj:
        """
        Set a radius for the search in the query. The radius is a float value that
        determines the maximum distance to the input vector in the search.
        A lower radius value means that the enforced maximum distance is lower,
        therefore closer vectors are returned only.
        A radius of 0.05 means the lowest cosine similarity of items returned to the query vector is 0.95.
        The valid range is between 0 and 1. Otherwise it will raise ValueError.

        Args:
            radius (NumericParamType | None): The maximum distance of the returned items from the query vector.
            If None, all results are returned.

        Returns:
            Self: The query object itself.

        Raises:
            ValueError: If the radius is not between 0 and 1.
        """
        radius_param = ParamInfo.init_with(ParamGroup.RADIUS, radius)
        return self.__alter(AlterParams(radius_param=radius_param))

    def with_vector(
        self,
        schema_obj: IdSchemaObject | T,
        id_param: ParamType,
        weight: NumericParamType = constants.DEFAULT_WEIGHT,
    ) -> QueryObj:
        """
        Add a 'with_vector' clause to the query. This fetches an object with id_param
        from the db and uses the vector of that item for search purposes. Weighting
        happens at the space level (and if there is also a .similar query present,
        this part has weight=1 compared to the weight set at .similar for the query
        vector).

        Args:
            weight (NumericParamType): Weight attributed to the vector retrieved via this clause in the aggregated
                query.
            schema_obj (SchemaObject | T): The schema object the vector is originating from.
            id_param (ParamType): The ID parameter. Eventually it is the ID of the vector to be used in the query.

        Returns:
            Self: The query object itself.
        """
        if not isinstance(schema_obj, IdSchemaObject):
            raise InvalidSchemaException(
                f"'with_vector': {type(self.schema)} is not a schema."
            )
        if self.query_filter_info.looks_like_filter_info is not None:
            raise QueryException(
                "One query cannot have more than one 'with vector' filter."
            )
        looks_like_filter_param = WeightedParamInfo.init_with(
            ParamGroup.LOOKS_LIKE_FILTER_VALUE,
            ParamGroup.LOOKS_LIKE_FILTER_WEIGHT,
            id_param,
            weight,
            schema_obj.id,
        )
        looks_like_filter_information = LooksLikeFilterInformation(schema_obj.id)
        return self.__alter(
            AlterParams(
                looks_like_filter_param=looks_like_filter_param,
                looks_like_filter_info=looks_like_filter_information,
            )
        )

    def filter(
        self,
        comparison_operation: ComparisonOperation[SchemaField] | _Or,
    ) -> QueryObj:
        """
        Add a 'filter' clause to the query. This filters the results from the db
        to only contain items based on the filtering input.
        E.g:
        filter(color_schema.color == "blue")
        filter(color_schema.color == Param("color_param"))
        filter(color_schema.color != "red")
        filter(color_schema.rating > 3)
        filter(color_schema.rating >= 3)
        filter(color_schema.rating < 3)
        filter(color_schema.rating <= 3)
        filter((color_schema.color == "blue") | (color_schema.color == "red"))
        filter(color_schema.categories.contains(["bright", "matte"]))
            - returns both bright and matte colors
        filter(color_schema.categories.not_contains(["bright", "matte"]))
            - returns colors that are non-bright and non-matte
        Args:
            comparison_operation ComparisonOperation[SchemaField]: The comparison operation.

        Returns:
            Self: The query object itself.
        """
        comparison_operations = (
            comparison_operation.operations
            if isinstance(comparison_operation, _Or)
            else [comparison_operation]
        )
        hard_filter_params_infos = [
            self._create_hard_filter_param_and_info(operation)
            for operation in comparison_operations
        ]
        hard_filter_params, hard_filter_infos = zip(*hard_filter_params_infos)
        return self.__alter(
            AlterParams(
                hard_filter_params=self.query_param_info.hard_filter_params
                + list(hard_filter_params),
                hard_filter_infos=self.query_filter_info.hard_filter_infos
                + list(hard_filter_infos),
            )
        )

    def _create_hard_filter_param_and_info(
        self, operation: ComparisonOperation
    ) -> tuple[ParamInfo, HardFilterInformation]:
        QueryFilterValidator.validate_operation_operand_type(
            operation, allow_param=True
        )
        hard_filter_param = ParamInfo.init_with(
            ParamGroup.HARD_FILTER,
            cast(ParamInputType, operation._other),
            cast(SchemaField, operation._operand),
            None,
            operation._op,
        )
        hard_filter_info = HardFilterInformation(
            operation._op,
            operation._operand,
            operation._group_key,
            hard_filter_param.name,
        )
        return hard_filter_param, hard_filter_info

    def __is_indexed_space(self, space: Space) -> bool:
        return self.index.has_space(space)

    def __is_space_bound(self, space: Space) -> bool:
        return any(
            similar_filter_info.space == space
            for similar_filter_info in self.query_filter_info.similar_filter_infos
        )

    def __alter(self, params: AlterParams) -> QueryObj:
        return QueryObj(
            self.index,
            self.schema,
            self.query_param_info.alter(
                params.space_weight_params,
                params.hard_filter_params,
                params.similar_filter_params,
                params.looks_like_filter_param,
                params.limit_param,
                params.radius_param,
                params.natural_query_param,
            ),
            self.query_filter_info.alter(
                params.hard_filter_infos,
                params.similar_filter_infos,
                params.looks_like_filter_info,
            ),
            params.override_now or self._override_now,
            params.natural_query_client_config or self.natural_query_client_config,
        )


class Query:
    """
    A class representing a query. Build queries using Params as placeholders for weights or query text,
    and supply their value later on when executing a query.

    Attributes:
        index (Index): The index.
        space_weight_map (Mapping[Space, NumericParamType] | None): The mapping of spaces to weights.
    """

    @TypeValidator.wrap
    def __init__(
        self,
        index: Index,
        weights: (
            Annotated[
                dict[Space, NumericParamType],
                TypeValidator.dict_validator(Space, NumericParamType),
            ]
            | None
        ) = None,
    ) -> None:
        """
        Initialize the Query.

        Args:
            index (Index): The index to be used for the query.
            weights (Mapping[Space, NumericParamType] | None, optional): The mapping of spaces to weights.
                Defaults to None, which is equal weight for each space.
        """
        self.index = index
        self._queries: list[QueryObj] = []
        self.weight_by_space = weights or {}

    def find(self, schema: IdSchemaObject | T) -> QueryObj:
        """
        Find a schema in the query.

        Args:
            schema (SchemaObject | T): The schema to find.

        Returns:
            QueryObj: The query object.

        Raises:
            InvalidSchemaException: If the schema is invalid.
            QueryException: If the index does not have the queried schema.
        """
        schema = self.__validate_and_cast_schema(schema)
        query_param_info = QueryParamInformation(
            space_weight_params=[
                ParamInfo.init_with(ParamGroup.SPACE_WEIGHT, weight, None, space)
                for space, weight in self.weight_by_space.items()
            ]
        )
        query_obj = QueryObj(self.index, schema, query_param_info)
        self._queries.append(query_obj)
        return query_obj

    def __validate_and_cast_schema(self, schema: IdSchemaObject | T) -> IdSchemaObject:
        if not isinstance(schema, IdSchemaObject):
            raise InvalidSchemaException(
                f"Invalid schema ({type(schema).__name__}) for find in {type(self).__name__}"
            )
        if not self.index.has_schema(schema):
            raise QueryException(
                f"Index doesn't have the queried schema ({schema._base_class_name})"
            )
        return schema
