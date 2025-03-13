Module superlinked.framework.dsl.query.query_clause.hard_filter_clause
======================================================================

Classes
-------

`HardFilterClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], op: ComparisonOperationType, operand: SchemaField, group_key: int | None)`
:   HardFilterClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], op: 'ComparisonOperationType', operand: 'SchemaField', group_key: 'int | None')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * abc.ABC

    ### Class variables

    `group_key: int | None`
    :

    `op: superlinked.framework.common.interface.comparison_operation_type.ComparisonOperationType`
    :

    `operand: superlinked.framework.common.schema.schema_object.SchemaField`
    :

    ### Static methods

    `from_param(operation: ComparisonOperation[SchemaField]) ‑> superlinked.framework.dsl.query.query_clause.hard_filter_clause.HardFilterClause`
    :

    ### Instance variables

    `is_type_mandatory_in_nlq: bool`
    :

    `nlq_annotations: list[NLQAnnotation]`
    :

    ### Methods

    `get_altered_knn_search_params(self, partial_params: KNNSearchClauseParams) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :