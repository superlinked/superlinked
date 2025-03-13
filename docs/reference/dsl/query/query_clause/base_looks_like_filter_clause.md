Module superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause
=================================================================================

Classes
-------

`BaseLooksLikeFilterClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], schema_field: IdField)`
:   BaseLooksLikeFilterClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], schema_field: 'IdField')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.looks_like_filter_clause.LooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.looks_like_filter_clause_weights_by_space.LooksLikeFilterClauseWeightBySpace

    ### Class variables

    `schema_field: superlinked.framework.common.schema.id_field.IdField`
    :

    ### Methods

    `get_altered_query_vector_params(self, query_vector_params: QueryVectorClauseParams, index_node_id: str, query_schema: IdSchemaObject, storage_manager: StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :