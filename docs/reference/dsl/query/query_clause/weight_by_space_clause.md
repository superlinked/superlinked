Module superlinked.framework.dsl.query.query_clause.weight_by_space_clause
==========================================================================

Classes
-------

`WeightBySpaceClause(space_weight_map: SpaceWeightMap = <factory>)`
:   WeightBySpaceClause(space_weight_map: 'SpaceWeightMap' = <factory>)

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * abc.ABC

    ### Class variables

    `space_weight_map: superlinked.framework.dsl.query.query_clause.space_weight_map.SpaceWeightMap`
    :

    ### Static methods

    `from_params(weight_param_by_space: Mapping[Space, NumericParamType], all_space: Sequence[Space]) ‑> superlinked.framework.dsl.query.query_clause.weight_by_space_clause.WeightBySpaceClause`
    :

    ### Instance variables

    `annotation_by_space_annotation: dict[str, str]`
    :

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    ### Methods

    `add_missing_space_weight_params(self, all_space: Sequence[Space]) ‑> Self`
    :

    `extend(self, weight_param_by_space: Mapping[Space, NumericParamType], all_space: Sequence[Space]) ‑> Self`
    :

    `get_altered_query_vector_params(self, query_vector_params: QueryVectorClauseParams, index_node_id: str, query_schema: IdSchemaObject, storage_manager: StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :

    `get_space_weight_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space, str]`
    :