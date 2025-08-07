Module superlinked.framework.dsl.query.query_clause.select_clause
=================================================================

Classes
-------

`SelectClause(value_param: superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam], schema: IdSchemaObject, vector_parts: Sequence[Space], fields_to_exclude: Sequence[SchemaField])`
:   SelectClause(value_param: Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]], schema: 'IdSchemaObject', vector_parts: 'Sequence[Space]', fields_to_exclude: 'Sequence[SchemaField]')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.single_value_param_query_clause.SingleValueParamQueryClause
    * superlinked.framework.dsl.query.query_clause.query_clause.QueryClause
    * abc.ABC

    ### Static methods

    `from_param(schema: IdSchemaObject, fields: Param | Sequence[str] | Sequence[SchemaField], vector_parts: Sequence[Space], fields_to_exclude: Sequence[SchemaField]) ‑> superlinked.framework.dsl.query.query_clause.select_clause.SelectClause`
    :

    ### Instance variables

    `fields_to_exclude: Sequence[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    `schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    `vector_parts: Sequence[superlinked.framework.dsl.space.space.Space]`
    :

    ### Methods

    `get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :

    `get_altered_metadata_extraction_params(self, metadata_extraction_params: MetadataExtractionClauseParams) ‑> superlinked.framework.dsl.query.clause_params.MetadataExtractionClauseParams`
    :