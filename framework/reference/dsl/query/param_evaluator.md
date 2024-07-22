Module superlinked.framework.dsl.query.param_evaluator
======================================================

Classes
-------

`EvaluatedParamInfo(limit: int, radius: float | None, space_weight_map: dict[superlinked.framework.dsl.space.space.Space, float], hard_filters: list[superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField]], similar_filters: dict[superlinked.framework.dsl.space.space.Space, list[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.SimilarPredicate]]], looks_like_filter: Optional[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.LooksLikePredicate]], natural_language_query_params: superlinked.framework.dsl.query.natural_language_query_param_handler.NaturalLanguageQueryParams)`
:   EvaluatedParamInfo(limit: int, radius: float | None, space_weight_map: dict[superlinked.framework.dsl.space.space.Space, float], hard_filters: list[superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField]], similar_filters: dict[superlinked.framework.dsl.space.space.Space, list[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.SimilarPredicate]]], looks_like_filter: Optional[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.LooksLikePredicate]], natural_language_query_params: superlinked.framework.dsl.query.natural_language_query_param_handler.NaturalLanguageQueryParams)

    ### Class variables

    `hard_filters: list[superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField]]`
    :

    `limit: int`
    :

    `looks_like_filter: Optional[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.LooksLikePredicate]]`
    :

    `natural_language_query_params: superlinked.framework.dsl.query.natural_language_query_param_handler.NaturalLanguageQueryParams`
    :

    `radius: float | None`
    :

    `similar_filters: dict[superlinked.framework.dsl.space.space.Space, list[superlinked.framework.dsl.query.predicate.binary_predicate.EvaluatedBinaryPredicate[superlinked.framework.dsl.query.predicate.binary_predicate.SimilarPredicate]]]`
    :

    `space_weight_map: dict[superlinked.framework.dsl.space.space.Space, float]`
    :