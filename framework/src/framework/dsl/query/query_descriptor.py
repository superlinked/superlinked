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

from collections.abc import Mapping

import structlog
from beartype.typing import Any, Sequence, Type, cast

from superlinked.framework.common.const import constants
from superlinked.framework.common.exception import (
    InvalidSchemaException,
    QueryException,
)
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
    _Or,
)
from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.nlq.open_ai import OpenAIClientConfig
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import (
    SchemaField,
    String,
    StringList,
)
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.nlq.nlq_handler import NLQHandler
from superlinked.framework.dsl.query.nlq.suggestion.query_suggestion_model import (
    QuerySuggestionsModel,
)
from superlinked.framework.dsl.query.param import (
    IntParamType,
    NumericParamType,
    Param,
    ParamInputType,
    ParamType,
    StringParamType,
)
from superlinked.framework.dsl.query.predicate.binary_predicate import (
    EvaluatedBinaryPredicate,
    LooksLikePredicate,
)
from superlinked.framework.dsl.query.query_clause import (
    HardFilterClause,
    LimitClause,
    LooksLikeFilterClause,
    NLQClause,
    NLQSystemPromptClause,
    OverriddenNowClause,
    QueryClause,
    QueryClauseT,
    RadiusClause,
    SelectClause,
    SimilarFilterClause,
    SpaceWeightClause,
    WeightedQueryClause,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.has_space_field_set import HasSpaceFieldSet
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

logger = structlog.getLogger()


@TypeValidator.wrap
class QueryDescriptor:  # pylint: disable=too-many-public-methods
    """
    A class representing a query object. Use .with_vector to run queries using a stored
    vector, or use .similar for queries where you supply the query at query-time. Or combine
    them, or even combine multiple .similar to supply different queries for each space in the
    Index.
    """

    def __init__(
        self,
        index: Index,
        schema: IdSchemaObject,
        clauses: Sequence[QueryClause] | None = None,
    ) -> None:
        self.__index = index
        self.__schema = schema
        self.__clauses: Sequence[QueryClause] = clauses if clauses else []
        QueryDescriptorValidator.validate(self)

    @property
    def clauses(self) -> Sequence[QueryClause]:
        return self.__clauses

    @property
    def index(self) -> Index:
        return self.__index

    @property
    def schema(self) -> IdSchemaObject:
        return self.__schema

    def space_weights(self, weight_by_space: Mapping[Space, NumericParamType]) -> QueryDescriptor:
        clauses = [SpaceWeightClause(self.__to_param(weight), space) for space, weight in weight_by_space.items()]
        altered_query_descriptor = self.__append_clauses(clauses)
        return altered_query_descriptor

    def override_now(self, now: IntParamType) -> QueryDescriptor:
        clause = OverriddenNowClause(self.__to_param(now))
        altered_query_descriptor = self.__append_clause(clause)
        return altered_query_descriptor

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
        field_set = (
            space_field_set.space_field_set if isinstance(space_field_set, HasSpaceFieldSet) else space_field_set
        )
        self.__validate_schema(field_set)
        value_param = self.__to_param(param)
        weight_param = self.__to_param(weight)
        clause = SimilarFilterClause(value_param, weight_param, field_set)
        altered_query_descriptor = self.__append_clause(clause)
        return altered_query_descriptor

    def __validate_schema(self, field_set: SpaceFieldSet) -> None:
        if self.schema not in field_set.space._embedding_node_by_schema:
            raise InvalidSchemaException(f"'find' ({type(self.schema)}) is not in similarity field's schema types.")

    def limit(self, limit: IntParamType | None) -> QueryDescriptor:
        """
        Set a limit to the number of results returned by the query.
        If the limit is None, -1 will be used, which is not handled by all databases.

        Args:
            limit (IntParamType): The maximum number of results to return.
        Returns:
            Self: The query object itself.
        """
        param = self.__to_param(limit) if limit is not None else Param.init_default(constants.DEFAULT_LIMIT)
        clause = LimitClause(param)
        altered_query_descriptor = self.__append_clause(clause)
        return altered_query_descriptor

    def select(self, *fields: SchemaField | str | Param) -> QueryDescriptor:
        """
        Select specific fields from the schema to be returned in the query results.

        Args:
            *fields (SchemaField | str | Param): The fields to select. Can be:
                - One or more SchemaField objects
                - One or more field names as strings
                - A single Param object that will be filled with fields later
                If no fields are provided, returns an empty selection.

        Returns:
            Self: The query object itself.

        Raises:
            QueryException: If multiple Param objects are provided or Param is mixed with other field types.
            TypeException: If any of the fields are of unsupported types.
            FieldException: If any of the schema fields are not part of the schema.
        """
        param = self.__handle_select_param(list(fields))
        clause = SelectClause(param)
        altered_query_descriptor = self.__append_clause(clause)
        return altered_query_descriptor

    def __handle_select_param(self, fields: Sequence[SchemaField | str | Param]) -> Param | Evaluated[Param]:
        if len(fields) == 0:
            return Param.init_evaluated([])
        if len(fields) == 1 and isinstance(fields[0], Param):
            return fields[0]
        if any(isinstance(item, Param) for item in fields):
            raise QueryException("Query select clause can only contain either a single Param or non-Param fields.")
        field_names = [field.name if isinstance(field, SchemaField) else field for field in fields]
        return self.__to_param(field_names)

    def select_all(self) -> QueryDescriptor:
        """
        Select all fields from the schema to be returned in the query results.

        Returns:
            Self: The query object itself.
        """
        return self.select(*self.__schema.schema_fields)

    def with_natural_query(
        self,
        natural_query: StringParamType,
        client_config: OpenAIClientConfig,
        system_prompt: StringParamType | None = None,
    ) -> QueryDescriptor:
        """
        Sets a natural language query based on which empty Params will have values set.

        Args:
            natural_query (StringParamType): Query containing desired characteristics.
            client_config (OpenAIClientConfig): Client config to initialize the client with.
            system_prompt (StringParamType | None): Custom system prompt to use for the query. Defaults to None.
        Returns:
            Self: The query object itself.
        """
        param = self.__to_param(natural_query)
        clauses: list[QueryClause] = [NLQClause(param, client_config)]
        if system_prompt:
            clauses.append(NLQSystemPromptClause(self.__to_param(system_prompt)))
        altered_query_descriptor = self.__append_clauses(clauses)
        self.__warn_if_nlq_is_used_without_recommended_param_descriptions(altered_query_descriptor)
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
        param = self.__to_param(radius) if radius is not None else Param.init_default()
        clause = RadiusClause(param)
        return self.__append_clause(clause)

    def with_vector(
        self,
        schema_obj: IdSchemaObject,
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
        value_param = self.__to_param(id_param)
        weight_param = self.__to_param(weight)
        clause = LooksLikeFilterClause(value_param, weight_param, schema_obj.id)
        return self.__append_clause(clause)

    def filter(self, comparison_operation: ComparisonOperation[SchemaField] | _Or) -> QueryDescriptor:
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
        filter(color_schema.categories.contains_all(["bright", "blue"]))
            - returns colors that are bright and blue at the same time
        Args:
            comparison_operation ComparisonOperation[SchemaField]: The comparison operation.

        Returns:
            Self: The query object itself.
        """
        comparison_operations = (
            comparison_operation.operations if isinstance(comparison_operation, _Or) else [comparison_operation]
        )
        for operation in comparison_operations:
            QueryFilterValidator.validate_operation_operand_type(operation, allow_param=True)
        clauses = [
            HardFilterClause(
                self.__to_param(operation._other),
                operation._op,
                cast(SchemaField, operation._operand),
                operation._group_key,
            )
            for operation in comparison_operations
        ]
        altered_query_descriptor = self.__append_clauses(clauses)
        self.__warn_if_nlq_is_used_without_recommended_param_descriptions(altered_query_descriptor)
        return altered_query_descriptor

    def nlq_suggestions(self, feedback: str | None = None) -> QuerySuggestionsModel:
        """
        Get suggestions for improving the natural language query parameters.

        This method analyzes the current query parameters and provides suggestions for improvement,
        including parameter naming, clarity, and overall query structure improvements.
        It requires that a natural language query has been set using with_natural_query().

        Args:
            feedback (str | None, optional): Additional feedback from the query creator to help
                generate more targeted suggestions. For example, you might provide context about
                specific requirements or constraints. Defaults to None.

        Returns:
            QuerySuggestionsModel: A model containing improvement suggestions and clarifying questions.
                You can access the suggestions directly via the model's attributes or call
                .print() for a formatted display of the suggestions.

                Example usage:
                ```python
                suggestions = query.nlq_suggestions()
                suggestions.print()  # Prints formatted suggestions
                # Or access directly:
                print(suggestions.improvement_suggestions)
                print(suggestions.clarifying_questions)
                ```

        Raises:
            QueryException: If with_natural_query() has not been called before this method.
        """
        nlq_clause = self.get_clause_by_type(NLQClause)
        if nlq_clause is None:
            raise QueryException("with_natural_query clause must be provided before calling nlq_suggestions")
        nlq_system_prompt_clause = self.get_clause_by_type(NLQSystemPromptClause)
        system_prompt = nlq_system_prompt_clause.evaluate() if nlq_system_prompt_clause is not None else None
        natural_query = nlq_clause.evaluate()
        return NLQHandler.suggest_improvements(
            self.clauses,
            natural_query,
            feedback,
            nlq_clause.client_config,
            system_prompt,
        )

    def get_limit(self) -> int:
        return self.get_mandatory_clause_by_type(LimitClause).evaluate()

    def get_radius(self) -> float | None:
        return self.get_mandatory_clause_by_type(RadiusClause).evaluate()

    def get_selected_fields(self) -> Sequence[SchemaField]:
        field_names = self.get_mandatory_clause_by_type(SelectClause).evaluate()
        return self.schema._get_fields_by_names(field_names)

    def get_hard_filters(self) -> list[ComparisonOperation[SchemaField]]:
        return [
            hard_filter
            for clause in self.get_clauses_by_type(HardFilterClause)
            if (hard_filter := clause.evaluate()) is not None
        ]

    def get_weights_by_space(self) -> dict[Space, float]:
        return dict(clause.evaluate() for clause in self.get_clauses_by_type(SpaceWeightClause))

    def get_looks_like_filter(
        self,
    ) -> EvaluatedBinaryPredicate[LooksLikePredicate] | None:
        looks_like_clause = self.get_clause_by_type(LooksLikeFilterClause)
        looks_like_filter = looks_like_clause.evaluate() if looks_like_clause is not None else None
        return looks_like_filter

    def get_similar_filters_spaces(self) -> list[Space]:
        evaluation_results = [clause.evaluate() for clause in self.get_clauses_by_type(SimilarFilterClause)]
        return [result[0] for result in evaluation_results if result is not None]

    def get_context_time(self, default: int | Any) -> int:
        if (overridden_now_clause := self.get_clause_by_type(OverriddenNowClause)) is not None:
            context_time = overridden_now_clause.evaluate()
        else:
            context_time = default
        if not isinstance(context_time, int):
            raise QueryException(f"'now' should be int, got {type(context_time).__name__}.")
        return context_time

    def append_missing_mandatory_clauses(self) -> QueryDescriptor:
        clauses: list[QueryClause] = []
        if self.get_clause_by_type(LimitClause) is None:
            clauses.append(LimitClause(Param.init_evaluated(constants.DEFAULT_LIMIT)))
        if self.get_clause_by_type(RadiusClause) is None:
            clauses.append(RadiusClause(Param.init_evaluated(None)))
        if self.get_clause_by_type(SelectClause) is None:
            clauses.append(SelectClause(Param.init_evaluated([])))
        missing_spaces = self._calculate_missing_spaces()
        clauses.extend(SpaceWeightClause(Param.init_default(), space) for space in missing_spaces)
        return self.__append_clauses(clauses)

    def _calculate_missing_spaces(self) -> list[Space]:
        spaces_with_weights = {clause.space for clause in self.get_clauses_by_type(SpaceWeightClause)}
        return [space for space in self.index._spaces if space not in spaces_with_weights]

    def get_param_value_to_set_for_unset_space_weight_clauses(self) -> dict[str, float]:
        unset_space_by_param_name = {
            clause.value_param.name: clause.space
            for clause in self.get_clauses_by_type(SpaceWeightClause)
            if not isinstance(clause.value_param, Evaluated)
        }
        if self.get_looks_like_filter() is not None:
            return {param_name: constants.DEFAULT_WEIGHT for param_name in unset_space_by_param_name.keys()}
        similar_filter_spaces = self.get_similar_filters_spaces()
        return {
            param_name: (
                constants.DEFAULT_WEIGHT if space in similar_filter_spaces else constants.DEFAULT_NOT_AFFECTING_WEIGHT
            )
            for param_name, space in unset_space_by_param_name.items()
        }

    def get_clause_by_type(self, clause_type: Type[QueryClauseT]) -> QueryClauseT | None:
        clauses = self.get_clauses_by_type(clause_type)
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        raise QueryException(f"Query cannot have more than one {clause_type.__name__}, got {len(clauses)}.")

    def get_mandatory_clause_by_type(self, clause_type: Type[QueryClauseT]) -> QueryClauseT:
        clause = self.get_clause_by_type(clause_type)
        if clause is None:
            raise QueryException(f"Query does not have mandatory clause: {clause_type.__name__}.")
        return clause

    def get_clauses_by_type(self, clause_type: Type[QueryClauseT]) -> list[QueryClauseT]:
        return [clause for clause in self.clauses if isinstance(clause, clause_type)]

    def replace_clauses(self, clauses: Sequence[QueryClause]) -> QueryDescriptor:
        return QueryDescriptor(self.index, self.schema, clauses)

    def get_weighted_clauses(self) -> list[WeightedQueryClause]:
        return [clause for clause in self.clauses if isinstance(clause, WeightedQueryClause)]

    def __append_clause(self, clause: QueryClause) -> QueryDescriptor:
        return self.__append_clauses([clause])

    def __append_clauses(self, clauses: Sequence[QueryClause]) -> QueryDescriptor:
        return QueryDescriptor(self.index, self.schema, list(self.clauses) + list(clauses))

    @classmethod
    def __to_param(cls, param_input: Any) -> Param | Evaluated[Param]:
        param_input = cast(ParamInputType, param_input)
        if not isinstance(param_input, Param):
            param_input = Param.init_evaluated(param_input)
        return param_input

    @classmethod
    def __warn_if_nlq_is_used_without_recommended_param_descriptions(cls, query_descriptor: QueryDescriptor) -> None:
        if not query_descriptor.get_clauses_by_type(NLQClause):
            return
        fields: set[SchemaField] = {field for space in query_descriptor.index._spaces for field in space._field_set}
        affected_param_names = [
            clause.value_param.name
            for clause in query_descriptor.get_clauses_by_type(HardFilterClause)
            if (
                isinstance(clause.value_param, Param)
                and clause.value_param.description is None
                and isinstance(clause.operand, (String, StringList))
                and clause.operand not in fields
            )
        ]
        if affected_param_names:
            affected_param_names_text = ", ".join(affected_param_names)
            logger.warning(
                f"When using a natural language query with a 'filter' for a field that has no corresponding"
                f" {type(CategoricalSimilaritySpace).__name__} and has a Param as a value,"
                f" it is recommended to provide a description for the Param that outlines the possible values."
                f" affected parameters: {affected_param_names_text}"
            )


class QueryDescriptorValidator:
    @staticmethod
    def validate(query_descriptor: QueryDescriptor) -> None:
        QueryDescriptorValidator.__validate_schema(query_descriptor)
        QueryDescriptorValidator.__validate_space_weight_clauses(query_descriptor)
        QueryDescriptorValidator.__validate_similar_clauses(query_descriptor)
        QueryDescriptorValidator.__validate_looks_like_filter_clause(query_descriptor)
        QueryDescriptorValidator.__validate_limit_clause(query_descriptor)
        QueryDescriptorValidator.__validate_radius_clause(query_descriptor)
        QueryDescriptorValidator.__validate_select_clause(query_descriptor)
        QueryDescriptorValidator.__validate_overridden_now_clause(query_descriptor)
        QueryDescriptorValidator.__validate_weighted_clauses(query_descriptor)

    @staticmethod
    def __validate_schema(query_descriptor: QueryDescriptor) -> None:
        if not query_descriptor.index.has_schema(query_descriptor.schema):
            raise QueryException(f"Index doesn't have the queried schema ({query_descriptor.schema._base_class_name})")

    @staticmethod
    def __validate_space_weight_clauses(query_descriptor: QueryDescriptor) -> None:
        clauses = query_descriptor.get_clauses_by_type(SpaceWeightClause)
        spaces = set()
        for clause in clauses:
            if clause.space in spaces:
                raise QueryException(
                    f"Attempted to bound space weight for {type(clause.space).__name__} in Query multiple times."
                )
            spaces.add(clause.space)
            clause.get_value()  # This also validates
        for space in spaces:
            if not query_descriptor.index.has_space(space):
                raise QueryException(f"Space isn't present in the index: {type(space).__name__}.")

    @staticmethod
    def __validate_similar_clauses(query_descriptor: QueryDescriptor) -> None:
        clauses = query_descriptor.get_clauses_by_type(SimilarFilterClause)
        for space in [clause.field_set.space for clause in clauses]:
            if not space.allow_similar_clause:
                raise QueryException(
                    f"Similar clause is not possible for {type(space).__name__} as the space configuration implies it."
                )
            if not query_descriptor.index.has_space(space):
                raise QueryException(f"Space isn't present in the index: {type(space).__name__}.")

    @staticmethod
    def __validate_looks_like_filter_clause(query_descriptor: QueryDescriptor) -> None:
        clause = query_descriptor.get_clause_by_type(LooksLikeFilterClause)
        if clause is None:
            return
        if not isinstance(clause.schema_field.schema_obj, IdSchemaObject):
            raise InvalidSchemaException(
                f"'with_vector': {type(clause.schema_field.schema_obj).__name__} is not a schema."
            )
        expected_type = GenericClassUtil.get_single_generic_type(clause.schema_field)
        if (value := clause.get_value()) is not None and not isinstance(value, expected_type):
            raise QueryException(
                f"Unsupported with_vector operand type: {type(value).__name__}, expected {expected_type.__name__}."
            )

    @staticmethod
    def __validate_limit_clause(query_descriptor: QueryDescriptor) -> None:
        clause = query_descriptor.get_clause_by_type(LimitClause)
        if clause is None:
            return
        clause.get_value()  # this also validates

    @staticmethod
    def __validate_radius_clause(query_descriptor: QueryDescriptor) -> None:
        clause = query_descriptor.get_clause_by_type(RadiusClause)
        if clause is None:
            return
        radius = clause.get_value()
        if radius is None:
            return
        if radius > constants.RADIUS_MAX or radius < constants.RADIUS_MIN:
            raise ValueError(
                f"Not a valid Radius value ({radius}). It should be between "
                f"{constants.RADIUS_MAX} and {constants.RADIUS_MIN}."
            )

    @staticmethod
    def __validate_select_clause(query_descriptor: QueryDescriptor) -> None:
        clause = query_descriptor.get_clause_by_type(SelectClause)
        if clause is None:
            return
        field_names = clause.get_value()
        query_descriptor.schema._get_fields_by_names(field_names)  # this also validates

    @staticmethod
    def __validate_overridden_now_clause(query_descriptor: QueryDescriptor) -> None:
        query_descriptor.get_clause_by_type(OverriddenNowClause)

    @staticmethod
    def __validate_weighted_clauses(query_descriptor: QueryDescriptor) -> None:
        clauses = [clause for clause in query_descriptor.clauses if isinstance(clause, WeightedQueryClause)]
        for clause in clauses:
            weight = clause.get_param_value(clause.weight_param)
            if weight is not None and not isinstance(weight, (int, float)):
                raise QueryException(f"Query clause weight should be numeric, got {type(weight).__name__}")
