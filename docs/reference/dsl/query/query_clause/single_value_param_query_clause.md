Module superlinked.framework.dsl.query.query_clause.single_value_param_query_clause
===================================================================================

Classes
-------

`SingleValueParamQueryClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam])`
:   SingleValueParamQueryClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]])

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause.BaseLooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.hard_filter_clause.HardFilterClause
    * superlinked.framework.dsl.query.query_clause.limit_clause.LimitClause
    * superlinked.framework.dsl.query.query_clause.nlq_clause.NLQClause
    * superlinked.framework.dsl.query.query_clause.nlq_system_prompt_clause.NLQSystemPromptClause
    * superlinked.framework.dsl.query.query_clause.overriden_now_clause.OverriddenNowClause
    * superlinked.framework.dsl.query.query_clause.radius_clause.RadiusClause
    * superlinked.framework.dsl.query.query_clause.select_clause.SelectClause
    * superlinked.framework.dsl.query.query_clause.similar_filter_clause.SimilarFilterClause

    ### Instance variables

    `params: Sequence[superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]]`
    :

    `value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Methods

    `get_altered_query_vector_params(self, query_vector_params: superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams, index_node_id: str, query_schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, storage_manager: superlinked.framework.common.storage_manager.storage_manager.StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :