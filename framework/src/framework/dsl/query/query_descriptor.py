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

import structlog
from beartype.typing import Mapping, NamedTuple, cast

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
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    String,
    StringList,
)
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
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.has_space_field_set import HasSpaceFieldSet
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["AlterParams"] = False

logger = structlog.getLogger()


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
class QueryDescriptor:  # pylint: disable=too-many-instance-attributes
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
        Initialize the QueryDescriptor.

        Args:
            builder (Query): The query builder.
            schema (IdSchemaObject): The schema object.
        """
        if not index.has_schema(schema):
            raise QueryException(
                f"Index doesn't have the queried schema ({schema._base_class_name})"
            )
        self.index = index
        self.schema = schema
        self._override_now = override_now
        self.natural_query_client_config = natural_query_client_config
        self.query_param_info = query_param_info or QueryParamInformation()
        self.query_filter_info = query_filter_info or QueryFilterInformation()

    @classmethod
    def init(
        cls,
        index: Index,
        schema: IdSchemaObject,
        weight_by_space: Mapping[Space, NumericParamType],
    ) -> QueryDescriptor:
        query_param_info = QueryParamInformation(
            space_weight_params=[
                ParamInfo.init_with(ParamGroup.SPACE_WEIGHT, weight, None, space)
                for space, weight in weight_by_space.items()
            ]
        )
        return QueryDescriptor(index, schema, query_param_info)

    def override_now(self, now: int) -> QueryDescriptor:
        return self.__alter(AlterParams(override_now=now))

    def similar(
        self,
        space_field_set: HasSpaceFieldSet | SpaceFieldSet,
        param: ParamType,
        weight: NumericParamType = constants.DEFAULT_WEIGHT,
    ) -> QueryDescriptor:
        """
        Add a 'similar' clause to the query. Similar queries compile query inputs (like query text) into vectors
        using a space and then use the query_vector (weighted with weight param) to search
        in the referenced space of the index.

        Args:
            space_field_set (HasSpaceFieldSet | SpaceFieldSet): The space or field set to search within.
            param (ParamType): The parameter. Basically the query itself. It can be a fixed value,
            or a placeholder (Param) for later substitution.
            weight (NumericParamType, optional): The weight. Defaults to 1.0.

        Returns:
            Self: The query object itself.

        Raises:
            QueryException: If the space is already bound in the query.
            InvalidSchemaException: If the schema is not in the similarity field's schema types.
        """
        if isinstance(space_field_set, HasSpaceFieldSet):
            field_set = space_field_set.space_field_set
        elif isinstance(space_field_set, SpaceFieldSet):
            field_set = space_field_set
        else:
            raise TypeError(
                f"Similar clause space_field_set got invalid type: {type(space_field_set).__name__}."
            )

        if not self.__is_indexed_space(field_set.space):
            raise QueryException("Space isn't present in the index.")
        relevant_field = field_set.get_field_for_schema(self.schema)
        if not relevant_field:
            raise InvalidSchemaException(
                f"'find' ({type(self.schema)}) is not in similarity field's schema types."
            )
        if self.__is_space_bound(field_set.space, relevant_field):
            raise QueryException("Space attempted to bound in query multiple times.")
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

    def limit(self, limit: IntParamType | None) -> QueryDescriptor:
        """
        Set a limit to the number of results returned by the query.
        If the limit is None, -1 will be used, which is not handled by all databases.

        Args:
            limit (IntParamType): The maximum number of results to return.
        Returns:
            Self: The query object itself.
        """
        if self.query_param_info.limit_param is not None:
            raise QueryException("One query cannot have more than one 'limit'.")
        limit_param = ParamInfo.init_with(ParamGroup.LIMIT, limit)
        return self.__alter(AlterParams(limit_param=limit_param))

    def with_natural_query(
        self, natural_query: StringParamType, client_config: OpenAIClientConfig
    ) -> QueryDescriptor:
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
        altered_query_descriptor = self.__alter(
            AlterParams(
                natural_query_param=natural_query_param,
                natural_query_client_config=client_config,
            )
        )
        self._warn_if_nlq_is_used_without_recommended_param_descriptions(
            altered_query_descriptor
        )
        return altered_query_descriptor

    def radius(self, radius: NumericParamType | None) -> QueryDescriptor:
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
        if self.query_param_info.radius_param is not None:
            raise QueryException("One query cannot have more than one 'radius'.")
        return self.__alter(AlterParams(radius_param=radius_param))

    def with_vector(
        self,
        schema_obj: IdSchemaObject | T,
        id_param: ParamType,
        weight: NumericParamType = constants.DEFAULT_WEIGHT,
    ) -> QueryDescriptor:
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
        altered_query_descriptor = self.__alter(
            AlterParams(
                looks_like_filter_param=looks_like_filter_param,
                looks_like_filter_info=looks_like_filter_information,
            )
        )
        return altered_query_descriptor

    def filter(
        self,
        comparison_operation: ComparisonOperation[SchemaField] | _Or,
    ) -> QueryDescriptor:
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
        altered_query_descriptor = self.__alter(
            AlterParams(
                hard_filter_params=self.query_param_info.hard_filter_params
                + list(hard_filter_params),
                hard_filter_infos=self.query_filter_info.hard_filter_infos
                + list(hard_filter_infos),
            )
        )
        self._warn_if_nlq_is_used_without_recommended_param_descriptions(
            altered_query_descriptor
        )
        return altered_query_descriptor

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

    def __is_space_bound(self, space: Space, schema_field: SchemaField) -> bool:
        return any(
            similar_filter_info.space == space
            and isinstance(similar_filter_info.schema_field, type(schema_field))
            for similar_filter_info in self.query_filter_info.similar_filter_infos
        )

    def __alter(self, params: AlterParams) -> QueryDescriptor:
        return QueryDescriptor(
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

    @classmethod
    def _warn_if_nlq_is_used_without_recommended_param_descriptions(
        cls, query_descriptor: QueryDescriptor
    ) -> None:
        if (
            query_descriptor.natural_query_client_config is None
            or not query_descriptor.query_param_info.hard_filter_params
        ):
            return
        affected_param_names = [
            param.name
            for param in query_descriptor.query_param_info.hard_filter_params
            if (
                param.value is None
                and param.description is None
                and not isinstance(param.space, CategoricalSimilaritySpace)
                and isinstance(param.schema_field, (String, StringList))
            )
        ]
        if affected_param_names:
            affected_param_names_text = ", ".join(affected_param_names)
            logger.warning(
                f"When using a natural query with a 'filter' for a field that has no corresponding"
                f" {type(CategoricalSimilaritySpace).__name__} and has a Param as a value,"
                f" it is recommended to provide a description for the Param that outlines the possible values."
                f" affected parameters: {affected_param_names_text}"
            )
