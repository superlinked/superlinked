Module superlinked.framework.dsl.query.param_evaluator
======================================================

Classes
-------

`EvaluatedQueryParams(limit: int, radius: float | None, weight_param_by_space: dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.EvaluatedParam[float]], hard_filter_param_by_schema_field: dict[superlinked.framework.common.interface.comparison_operand.ComparisonOperand[superlinked.framework.common.schema.schema_object.SchemaField], superlinked.framework.dsl.query.param.EvaluatedParam[collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | bool | None]], similar_filter_by_space_by_schema_field: dict[superlinked.framework.common.schema.schema_object.SchemaField, dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.WeightedEvaluatedParam]], looks_like_filter_param: superlinked.framework.dsl.query.param.WeightedEvaluatedParam | None)`
:   EvaluatedQueryParams(limit: int, radius: float | None, weight_param_by_space: dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.EvaluatedParam[float]], hard_filter_param_by_schema_field: dict[superlinked.framework.common.interface.comparison_operand.ComparisonOperand[superlinked.framework.common.schema.schema_object.SchemaField], superlinked.framework.dsl.query.param.EvaluatedParam[collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | bool | None]], similar_filter_by_space_by_schema_field: dict[superlinked.framework.common.schema.schema_object.SchemaField, dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.WeightedEvaluatedParam]], looks_like_filter_param: superlinked.framework.dsl.query.param.WeightedEvaluatedParam | None)

    ### Class variables

    `hard_filter_param_by_schema_field: dict[superlinked.framework.common.interface.comparison_operand.ComparisonOperand[superlinked.framework.common.schema.schema_object.SchemaField], superlinked.framework.dsl.query.param.EvaluatedParam[collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | bool | None]]`
    :

    `limit: int`
    :

    `looks_like_filter_param: superlinked.framework.dsl.query.param.WeightedEvaluatedParam | None`
    :

    `radius: float | None`
    :

    `similar_filter_by_space_by_schema_field: dict[superlinked.framework.common.schema.schema_object.SchemaField, dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.WeightedEvaluatedParam]]`
    :

    `weight_param_by_space: dict[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.param.EvaluatedParam[float]]`
    :