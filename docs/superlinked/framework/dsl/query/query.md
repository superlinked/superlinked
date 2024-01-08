Module superlinked.framework.dsl.query.query
============================================

Classes
-------

`Query(index: Index, weights: Mapping[Space, FloatParamType] | None = None)`
:   A class representing a query. Build queries using Params as placeholders for weights or query text,
    and supply their value later on when executing a query.
    
    Attributes:
        index (Index): The index.
        space_weight_map (Mapping[Space, FloatParamType] | None): The mapping of spaces to weights.
    
    Initialize the Query.
    
    Args:
        index (Index): The index to be used for the query.
        weights (Mapping[Space, FloatParamType] | None, optional): The mapping of spaces to weights.
            Defaults to None, which is equal weight for each space.

    ### Methods

    `find(self, schema: IdSchemaObject | T) ‑> superlinked.framework.dsl.query.query.QueryObj`
    :   Find a schema in the query.
        
        Args:
            schema (SchemaObject | T): The schema to find.
        
        Returns:
            QueryObj: The query object.
        
        Raises:
            InvalidSchemaException: If the schema is invalid.
            QueryException: If the index does not have the queried schema.

`QueryObj(builder: Query, schema: IdSchemaObject | T)`
:   A class representing a query object. Use .with_vector to run queries using a stored
    vector, or use .similar for queries where you supply the query at query-time. Or combine
    them, or even combine multiple .similar to supply different queries for each space in the
    Index.
    
    Attributes:
        builder (Query): The query builder.
        schema (SchemaObject): The schema object.
        index (Index): The index.
        filters (list[QueryPredicate]): The list of query predicates.
        _limit (int | None): The limit for the query. If None, no limit is applied.
            The default is 100, to disable it, add the .limit(None) to the query.
        _radius (float | None): The radius for the query. If None, no radius is applied.
            The float can be between 0 and 1. Otherwise ValueError is thrown
            The lower the number the closer the vectors are.
    
    Initialize the QueryObj.
    
    Args:
        builder (Query): The query builder.
        schema (SchemaObject | T): The schema object.

    ### Methods

    `limit(self, limit: int | None) ‑> typing_extensions.Self`
    :   Set a limit to the number of results returned by the query.
        If the limit is None, a result set based on all elements in the index will be returned.
        
        Args:
            limit (int | None): The maximum number of results to return. If None, all results are returned.
        
        Returns:
            Self: The query object itself.

    `override_now(self, now: int) ‑> typing_extensions.Self`
    :

    `radius(self, radius: float) ‑> typing_extensions.Self`
    :   Set a radius for the search in the query. The radius is a float value that
        determines the maximum distance to the input vector in the search.
        A lower radius value means that the enforced maximum distance is lower,
        therefore closer vectors are returned only.
        A radius of 0.05 means the lowest cosine similarity of items returned to the query vector is 0.95.
        The valid range is between 0 and 1. Otherwise it will raise ValueError.
        
        Args:
            radius (float): The maximum distance of the returned items from the query vector.
        
        Returns:
            Self: The query object itself.
        
        Raises:
            ValueError: If the radius is not between 0 and 1.

    `similar(self, field_set: SpaceFieldSet, param: ParamType, weight: FloatParamType = 1.0) ‑> typing_extensions.Self`
    :   Add a 'similar' clause to the query. Similar queries compile query inputs (like query text) into vectors
        using a space and then use the query_vector (weighted with weight param) to search
        in the referenced space of the index.
        
        Args:
            field_set (SpaceFieldSet): The referenced space.
            param (ParamType): The parameter. Basically the query itself. It can be a fixed value,
            or a placeholder (Param) for later substitution.
            weight (FloatParamType, optional): The weight. Defaults to 1.0.
        
        Returns:
            Self: The query object itself.
        
        Raises:
            QueryException: If the space is already bound in the query.
            InvalidSchemaException: If the schema is not in the similarity field's schema types.

    `with_vector(self, schema_obj: IdSchemaObject | T, id_param: ParamType) ‑> typing_extensions.Self`
    :   Add a 'with_vector' clause to the query. This fetches an object with id_param
        from the db and uses the vector of that item for search purposes. Weighting
        happens at the space level (and if there is also a .similar query present,
        this part has weight=1 compared to the weight set at .similar for the query
        vector).
        
        Args:
            schema_obj (SchemaObject | T): The schema object.
            id_param (ParamType): The ID parameter.
        
        Returns:
            Self: The query object itself.