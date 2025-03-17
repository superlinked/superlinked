Module superlinked.framework.dsl.query.query_clause.query_clause
================================================================

Classes
-------

`NLQCompatible()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.query.nlq.nlq_compatible_clause_handler.NLQCompatibleClauseHandler
    * superlinked.framework.dsl.query.query_clause.base_looks_like_filter_clause.BaseLooksLikeFilterClause
    * superlinked.framework.dsl.query.query_clause.hard_filter_clause.HardFilterClause
    * superlinked.framework.dsl.query.query_clause.similar_filter_clause.SimilarFilterClause
    * superlinked.framework.dsl.query.query_clause.weight_by_space_clause.WeightBySpaceClause

    ### Instance variables

    `annotation_by_space_annotation: dict[str, str]`
    :

    `is_type_mandatory_in_nlq: bool`
    :

    `nlq_annotations: list[NLQAnnotation]`
    :

    ### Methods

    `get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) ‑> set[collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | tuple[str | None, str | None] | None]`
    :

    `set_defaults_for_nlq(self) ‑> Self`
    :

`QueryClause()`
:   QueryClause()

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.weight_by_space_clause.WeightBySpaceClause

    ### Static methods

    `get_param(typed_param: TypedParam | Evaluated[TypedParam]) ‑> superlinked.framework.dsl.query.param.Param`
    :

    `get_typed_param(typed_param: TypedParam | Evaluated[TypedParam]) ‑> superlinked.framework.dsl.query.typed_param.TypedParam`
    :

    ### Instance variables

    `params: Sequence[TypedParam | Evaluated[TypedParam]]`
    :

    ### Methods

    `alter_param_values(self, param_values: Mapping[str, ParamInputType | None], is_override_set: bool) ‑> Self`
    :

    `get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :

    `get_altered_metadata_extraction_params(self, metadata_extraction_params: MetadataExtractionClauseParams) ‑> superlinked.framework.dsl.query.clause_params.MetadataExtractionClauseParams`
    :

    `get_altered_nql_params(self, nlq_clause_params: NLQClauseParams) ‑> superlinked.framework.dsl.query.clause_params.NLQClauseParams`
    :

    `get_altered_query_vector_params(self, query_vector_params: QueryVectorClauseParams, index_node_id: str, query_schema: IdSchemaObject, storage_manager: StorageManager) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :

    `get_default_value_by_param_name(self) ‑> dict[str, typing.Any]`
    :

    `get_param_value_by_param_name(self) ‑> dict[str, float | int | str | superlinked.framework.common.data_types.Vector | list[float] | list[str] | superlinked.framework.common.schema.blob_information.BlobInformation | None]`
    :

    `get_space_weight_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space, str]`
    :

    `get_weight_param_name_by_space(self) ‑> dict[superlinked.framework.dsl.space.space.Space | None, str]`
    :