Module superlinked.framework.dsl.query.clause_params
====================================================

Classes
-------

`KNNSearchClauseParams(limit: int | None = None, filters: Sequence[ComparisonOperation[SchemaField]] = <factory>, schema_fields_to_return: Sequence[SchemaField] = <factory>, radius: float | None = None, should_return_index_vector: bool = False)`
:   KNNSearchClauseParams(limit: 'int | None' = None, filters: 'Sequence[ComparisonOperation[SchemaField]]' = <factory>, schema_fields_to_return: 'Sequence[SchemaField]' = <factory>, radius: 'float | None' = None, should_return_index_vector: 'bool' = False)

    ### Instance variables

    `filters: Sequence[superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField]]`
    :

    `limit: int | None`
    :

    `radius: float | None`
    :

    `schema_fields_to_return: Sequence[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    `should_return_index_vector: bool`
    :

    ### Methods

    `set_params(self, **params: Any) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :

`MetadataExtractionClauseParams(vector_part_ids: Sequence[str] = <factory>)`
:   MetadataExtractionClauseParams(vector_part_ids: 'Sequence[str]' = <factory>)

    ### Instance variables

    `vector_part_ids: Sequence[str]`
    :

`NLQClauseParams(client_config: OpenAIClientConfig | None = None, natural_query: str | None = None, system_prompt: str | None = None)`
:   NLQClauseParams(client_config: 'OpenAIClientConfig | None' = None, natural_query: 'str | None' = None, system_prompt: 'str | None' = None)

    ### Instance variables

    `client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig | None`
    :

    `natural_query: str | None`
    :

    `system_prompt: str | None`
    :

`QueryVectorClauseParams(weight_by_space: Mapping[Space, float] = <factory>, context_time: int | None = None, query_node_inputs_by_node_id: Mapping[str, list[QueryNodeInput]] = <factory>)`
:   QueryVectorClauseParams(weight_by_space: 'Mapping[Space, float]' = <factory>, context_time: 'int | None' = None, query_node_inputs_by_node_id: 'Mapping[str, list[QueryNodeInput]]' = <factory>)

    ### Instance variables

    `context_time: int | None`
    :

    `query_node_inputs_by_node_id: Mapping[str, list[superlinked.framework.query.query_node_input.QueryNodeInput]]`
    :

    `weight_by_space: Mapping[superlinked.framework.dsl.space.space.Space, float]`
    :

    ### Methods

    `set_params(self, **params: Any) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :