Module superlinked.framework.dsl.query.query_descriptor
=======================================================

Classes
-------

`QueryDescriptor(index: superlinked.framework.dsl.index.index.Index, schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, clauses: collections.abc.Sequence[superlinked.framework.dsl.query.query_clause.query_clause.QueryClause] | None = None, query_user_config: superlinked.framework.dsl.query.query_user_config.QueryUserConfig | None = None)`
:   A class representing a query object. Use .with_vector to run queries using a stored
    vector, or use .similar for queries where you supply the query at query-time. Or combine
    them, or even combine multiple .similar to supply different queries for each space in the
    Index.

    ### Instance variables

    `clauses: Sequence[QueryClause]`
    :

    `index: Index`
    :

    `query_user_config: QueryUserConfig`
    :

    `schema: IdSchemaObject`
    :

    `with_metadata: bool`
    :

    ### Methods

    `append_missing_mandatory_clauses(self) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :

    `filter(self, comparison_operation: superlinked.framework.common.interface.comparison_operand.ComparisonOperation[superlinked.framework.common.schema.schema_object.SchemaField] | superlinked.framework.common.interface.comparison_operand._Or[superlinked.framework.common.schema.schema_object.SchemaField]) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Add a 'filter' clause to the query. This filters the results from the db
        to only contain items based on the filtering input.
        E.g:
        filter(color_schema.color == "blue")
        filter(color_schema.color == Param("color_param"))
        filter(color_schema.color != "red")
        filter(color_schema.rating > 3)
        filter(color_schema.rating >= 3)
        filter(color_schema.rating < 3)
        filter(color_schema.rating <= 3)
        filter((color_schema.color == "blue") | (color_schema.color == "red"))
        filter(color_schema.categories.contains(["bright", "matte"]))
            - returns both bright and matte colors
        filter(color_schema.categories.not_contains(["bright", "matte"]))
            - returns colors that are non-bright and non-matte
        filter(color_schema.categories.contains_all(["bright", "blue"]))
            - returns colors that are bright and blue at the same time
        Args:
            comparison_operation ComparisonOperation[SchemaField]: The comparison operation.
        
        Returns:
            Self: The query object itself.

    `get_clause_by_type(self, clause_type: Type[QueryClauseT]) ‑> ~QueryClauseT | None`
    :

    `get_clauses_by_type(self, clause_type: Type[QueryClauseT]) ‑> list[~QueryClauseT]`
    :

    `get_param_value_for_unset_space_weights(self) ‑> dict[str, float]`
    :

    `include_metadata(self) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Make per-item metadata to be returned in the query results.
        Current metadata includes space-wise partial scores.
        Returns:
            Self: The query object itself.

    `limit(self, limit: int | superlinked.framework.dsl.query.param.Param | None) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Set a limit to the number of results returned by the query.
        If the limit is None, -1 will be used, which is not handled by all databases.
        
        Args:
            limit (IntParamType): The maximum number of results to return.
        Returns:
            Self: The query object itself.

    `override_now(self, now: int | superlinked.framework.dsl.query.param.Param) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :

    `radius(self, radius: float | int | superlinked.framework.dsl.query.param.Param | None) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Set a radius for the search in the query. The radius is a float value that
        determines the maximum distance to the input vector in the search.
        A lower radius value means that the enforced maximum distance is lower,
        therefore closer vectors are returned only.
        A radius of 0.05 means the lowest cosine similarity of items returned to the query vector is 0.95.
        The valid range is between 0 and 1. Otherwise it will raise InvalidInputException.
        
        Args:
            radius (NumericParamType | None): The maximum distance of the returned items from the query vector.
            If None, all results are returned.
        
        Returns:
            Self: The query object itself.
        
        Raises:
            InvalidInputException: If the radius is not between 0 and 1.

    `replace_clauses(self, clauses: Sequence[QueryClause]) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :

    `replace_user_config(self, query_user_config: superlinked.framework.dsl.query.query_user_config.QueryUserConfig) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Replace the current query user configuration with a new one.
        
        This method allows you to set custom configuration options for the query execution,
        such as whether to include metadata in results or Redis-specific settings.
        
        Args:
            query_user_config (QueryUserConfig): The new configuration to use for this query.
        
        Returns:
            QueryDescriptor: A new query descriptor with the updated configuration.

    `select(self, fields: superlinked.framework.common.schema.schema_object.SchemaField | None | str | superlinked.framework.dsl.query.param.Param | collections.abc.Sequence[superlinked.framework.common.schema.schema_object.SchemaField | None | str | superlinked.framework.dsl.query.param.Param] = None, metadata: collections.abc.Sequence[superlinked.framework.dsl.space.space.Space] | None = None) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Select specific fields from the schema to be returned in the query results.
        
        Args:
            fields (SchemaFieldSelector | SchemaFieldSelector | None): The fields to select. Can be:
                - One or more SchemaField objects
                - One or more field names as strings
                - A single Param object that will be filled with fields later
                If no fields are provided, returns an empty selection.
            metadata (Sequence[Space] | None): The spaces identifying the requested vector parts.
                Defaults to None.
        Returns:
            Self: The query object itself.
        
        Raises:
            InvalidInputException:
                - If multiple Param objects are provided or Param is mixed with other field types.
                - If any of the fields are of unsupported types.
                - If any of the schema fields are not part of the schema.
                - If any of the spaces in metadata is not a Space.

    `select_all(self, metadata: collections.abc.Sequence[superlinked.framework.dsl.space.space.Space] | None = None) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Select all fields from the schema to be returned in the query results.
        
        Args:
            metadata (Sequence[Space] | None): The spaces identifying the requested vector parts.
                Defaults to None.
        
        Returns:
            Self: The query object itself.
        
        Raises:
            See `select`.

    `similar(self, space_field_set: superlinked.framework.dsl.space.has_space_field_set.HasSpaceFieldSet | superlinked.framework.dsl.space.space_field_set.SpaceFieldSet, param: collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | tuple[str | None, str | None] | None | superlinked.framework.dsl.query.param.Param, weight: float | int | superlinked.framework.dsl.query.param.Param = 1.0) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Add a 'similar' clause to the query. Similar queries compile query inputs (like query text) into vectors
        using a space and then use the query_vector (weighted with weight param) to search
        in the referenced space of the index.
        
        Args:
            space_field_set (HasSpaceFieldSet | SpaceFieldSet): The space or field set to search within.
            param (ParamType): The parameter. Basically the query itself. It can be a fixed value,
            or a placeholder (Param) for later substitution.
            weight (NumericParamType, optional): The weight. Defaults to 1.0.
        
        Returns:
            Self: The query object itself.
        
        Raises:
            InvalidInputException: If the space is already bound in the query.
            InvalidInputException: If the schema is not in the similarity field's schema types.

    `space_weights(self, weight_by_space: Mapping[superlinked.framework.dsl.space.space.Space, float | int | superlinked.framework.dsl.query.param.Param]) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :

    `with_natural_query(self, natural_query: str | superlinked.framework.dsl.query.param.Param, client_config: superlinked.framework.common.nlq.open_ai.OpenAIClientConfig, system_prompt: str | superlinked.framework.dsl.query.param.Param | None = None) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Sets a natural language query based on which empty Params will have values set.
        
        Args:
            natural_query (StringParamType): Query containing desired characteristics.
            client_config (OpenAIClientConfig): Client config to initialize the client with.
            system_prompt (StringParamType | None): Custom system prompt to use for the query. Defaults to None.
        Returns:
            Self: The query object itself.

    `with_vector(self, schema_obj: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, id_param: str | superlinked.framework.dsl.query.param.Param, weight: float | int | superlinked.framework.dsl.query.param.Param | collections.abc.Mapping[superlinked.framework.dsl.space.space.Space, float | int | superlinked.framework.dsl.query.param.Param] = 1.0) ‑> superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :   Add a 'with_vector' clause to the query. This fetches an object with id_param
        from the db and uses the vector of that item for search purposes. Weighting
        happens at the space level (and if there is also a .similar query present,
        this part has weight=1 compared to the weight set at .similar for the query
        vector).
        
        Args:
            schema_obj (IdSchemaObject): The schema object the vector is originating from.
            id_param (StringParamType): The ID parameter. Eventually it is the ID of the vector to be used in the query.
            weight (NumericParamType | Mapping[Space, NumericParamType]): Weight attributed to the vector
                retrieved via this clause in the aggregated query. Can be fine-tuned with space-wise weighting,
                but resolving missing per-space weights with NLQ is not supported.
        
        Returns:
            Self: The query object itself.

`QueryDescriptorValidator()`
:   

    ### Static methods

    `validate(query_descriptor: QueryDescriptor) ‑> None`
    :