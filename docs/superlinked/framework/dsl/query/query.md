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
        index (Index): The index.
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
    
    Initialize the QueryObj.
    
    Args:
        builder (Query): The query builder.
        schema (SchemaObject | T): The schema object.

    ### Methods

    `override_now(self, now: int) ‑> typing_extensions.Self`
    :

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