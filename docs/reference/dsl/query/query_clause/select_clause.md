Module superlinked.framework.dsl.query.query_clause.select_clause
=================================================================

Classes
-------

`SelectClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], schema: IdSchemaObject)`
:   SelectClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], schema: 'IdSchemaObject')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Class variables

    `schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    ### Static methods

    `from_param(schema: IdSchemaObject, param: Param | Sequence[str]) ‑> superlinked.framework.dsl.query.query_clause.select_clause.SelectClause`
    :

    ### Methods

    `get_altered_knn_search_params(self, partial_params: KNNSearchClauseParams) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :