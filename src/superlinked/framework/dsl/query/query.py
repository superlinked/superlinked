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

from typing import Annotated, TypedDict, cast

from superlinked.framework.common.const import DEFAULT_WEIGHT
from superlinked.framework.common.exception import (
    InvalidSchemaException,
    QueryException,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema import T
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import (
    IntParamType,
    NumericParamType,
    ParamType,
)
from superlinked.framework.dsl.query.predicate.binary_op import BinaryOp
from superlinked.framework.dsl.query.predicate.binary_predicate import BinaryPredicate
from superlinked.framework.dsl.query.predicate.query_predicate import QueryPredicate
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryObjInternalProperty"] = False


class QueryObjInternalProperty(TypedDict, total=False):
    """Only intended for self initialization inside QueryObj functions, not for external initialization"""

    filters: list[QueryPredicate]
    limit: IntParamType | None
    radius: NumericParamType | None
    override_now: int | None
    filtered_spaces: set[Space]


@TypeValidator.wrap
class QueryObj:
    """
    A class representing a query object. Use .with_vector to run queries using a stored
    vector, or use .similar for queries where you supply the query at query-time. Or combine
    them, or even combine multiple .similar to supply different queries for each space in the
    Index.

    Attributes:
        builder (Query): The query builder.
        schema (SchemaObject): The schema object.
    """

    def __init__(
        self,
        builder: Query,
        schema: IdSchemaObject,
        internal_property: QueryObjInternalProperty | None = None,
    ) -> None:
        """
        Initialize the QueryObj.

        Args:
            builder (Query): The query builder.
            schema (IdSchemaObject): The schema object.
        """
        self.builder = builder
        self.schema = cast(IdSchemaObject, schema)
        if not internal_property:
            internal_property = {}
        self.filters = internal_property.get("filters", list[QueryPredicate]())
        self.limit_ = internal_property.get("limit")
        self.radius_ = internal_property.get("radius")
        # by default now in queries is the system time, but it can be overridden for testing/reproducible notebooks
        self._override_now = internal_property.get("override_now")
        self.__filtered_spaces = internal_property.get("filtered_spaces", set[Space]())

    @property
    def index(self) -> Index:
        """
        The index the query is executed on.
        """
        return self.builder.index

    def override_now(self, now: int) -> QueryObj:
        return self.__alter({"override_now": now})

    def similar(
        self,
        field_set: SpaceFieldSet,
        param: ParamType,
        weight: NumericParamType = DEFAULT_WEIGHT,
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

        if relevant_field := field_set.get_field_for_schema(self.schema):
            similar_filter = BinaryPredicate(
                BinaryOp.SIMILAR,
                relevant_field,
                param,
                weight,
                field_set.space._get_node(self.schema),
            )
            filtered_spaces = self.__filtered_spaces.copy()
            filters = self.filters.copy()
            filtered_spaces.add(field_set.space)
            filters.append(similar_filter)
            return self.__alter(
                {"filters": filters, "filtered_spaces": filtered_spaces}
            )
        raise InvalidSchemaException(
            f"'find' ({type(self.schema)}) is not in similarity field's schema types."
        )

    def limit(self, limit: IntParamType | None) -> QueryObj:
        """
        Set a limit to the number of results returned by the query.
        If the limit is None, a result set based on all elements in the index will be returned.

        Args:
            limit (IntParamType | None): The maximum number of results to return. If None, all results are returned.

        Returns:
            Self: The query object itself.
        """
        return self.__alter({"limit": limit})

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
        return self.__alter({"radius": radius})

    def with_vector(
        self,
        schema_obj: IdSchemaObject | T,
        id_param: ParamType,
        weight: NumericParamType = DEFAULT_WEIGHT,
    ) -> QueryObj:
        """
        Add a 'with_vector' clause to the query. This fetches an object with id_param
        from the db and uses the vector of that item for search purposes. Weighting
        happens at the space level (and if there is also a .similar query present,
        this part has weight=1 compared to the weight set at .similar for the query
        vector).

        Args:
            schema_obj (SchemaObject | T): The schema object.
            id_param (ParamType): The ID parameter.

        Returns:
            Self: The query object itself.
        """
        if not isinstance(schema_obj, IdSchemaObject):
            raise InvalidSchemaException(
                f"'with_vector': {type(self.schema)} is not a schema."
            )
        filters = self.filters.copy()
        filters.append(
            BinaryPredicate(
                op=BinaryOp.LOOKS_LIKE,
                left_param=schema_obj.id,
                right_param=id_param,
                weight=weight,
            )
        )
        return self.__alter({"filters": filters})

    def __is_indexed_space(self, space: Space) -> bool:
        return self.builder.index.has_space(space)

    def __is_space_bound(self, space: Space) -> bool:
        return space in self.__filtered_spaces

    def __alter(self, properties: QueryObjInternalProperty) -> QueryObj:
        properties_use: QueryObjInternalProperty = {
            "filters": self.filters,
            "limit": self.limit_,
            "radius": self.radius_,
            "override_now": self._override_now,
            "filtered_spaces": self.__filtered_spaces,
        }
        properties_use.update(properties)
        return QueryObj(
            builder=self.builder,
            schema=self.schema,
            internal_property=properties_use,
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
        self.space_weight_map = weights or {}

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
        self.__validate_find_input(schema)
        query_obj = QueryObj(self, cast(IdSchemaObject, schema))
        self._queries.append(query_obj)
        return query_obj

    def __validate_find_input(self, schema: IdSchemaObject | T) -> None:
        if not isinstance(schema, IdSchemaObject):
            raise InvalidSchemaException(
                f"Invalid schema ({schema.__class__.__name__}) for find in {self.__class__.__name__}"
            )
        if not self.index.has_schema(schema):
            raise QueryException(
                f"Index doesn't have the queried schema ({schema._base_class_name})"
            )
