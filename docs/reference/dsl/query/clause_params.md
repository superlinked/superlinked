Module superlinked.framework.dsl.query.clause_params
====================================================

Classes
-------

`KNNSearchClauseParams(limit: int | None = None, filters: Sequence[ComparisonOperation[SchemaField]] = <factory>, schema_fields_to_return: Sequence[SchemaField] = <factory>, radius: float | None = None)`
:   KNNSearchClauseParams(limit: 'int | None' = None, filters: 'Sequence[ComparisonOperation[SchemaField]]' = <factory>, schema_fields_to_return: 'Sequence[SchemaField]' = <factory>, radius: 'float | None' = None)

    ### Class variables

    `filters: Sequence[superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField]]`
    :

    `limit: int | None`
    :

    `radius: float | None`
    :

    `schema_fields_to_return: Sequence[superlinked.framework.common.schema.schema_object.SchemaField]`
    :

    ### Methods

    `set_params(self, **params: Any) ‑> superlinked.framework.dsl.query.clause_params.KNNSearchClauseParams`
    :

`NLQClauseParams(client_config: OpenAIClientConfig | None = None, natural_query: str | None = None, system_prompt: str | None = None)`
:   NLQClauseParams(client_config: 'OpenAIClientConfig | None' = None, natural_query: 'str | None' = None, system_prompt: 'str | None' = None)

    ### Class variables

    `client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig | None`
    :

    `natural_query: str | None`
    :

    `system_prompt: str | None`
    :

`QueryVectorClauseParams(weight_by_space: Mapping[Space, float] = <factory>, context_time: int | None = None, query_node_inputs_by_node_id: Mapping[str, list[QueryNodeInput]] = <factory>)`
:   QueryVectorClauseParams(weight_by_space: 'Mapping[Space, float]' = <factory>, context_time: 'int | None' = None, query_node_inputs_by_node_id: 'Mapping[str, list[QueryNodeInput]]' = <factory>)

    ### Class variables

    `context_time: int | None`
    :

    `query_node_inputs_by_node_id: Mapping[str, list[superlinked.framework.query.query_node_input.QueryNodeInput]]`
    :

    `weight_by_space: Mapping[superlinked.framework.dsl.space.space.Space, float]`
    :

    ### Methods

    `set_params(self, **params: Any) ‑> superlinked.framework.dsl.query.clause_params.QueryVectorClauseParams`
    :