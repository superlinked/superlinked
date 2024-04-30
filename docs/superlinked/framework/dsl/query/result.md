Module superlinked.framework.dsl.query.result
=============================================

Classes
-------

`Result(schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, entries: list[superlinked.framework.dsl.query.result.ResultEntry])`
:   A class representing the result of a query.
    
    Attributes:
        schema (IdSchemaObject): The schema of the result.
        entries (list[ResultEntry]): A list of result entries.

    ### Class variables

    `entries: list[superlinked.framework.dsl.query.result.ResultEntry]`
    :

    `schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    ### Methods

    `to_pandas(self) ‑> pandas.core.frame.DataFrame`
    :   Converts the query result entries into a pandas DataFrame.
        
        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects.
        
        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects.

`ResultEntry(entity: superlinked.framework.storage.entity.Entity, stored_object: dict[str, typing.Any])`
:   Represents a single entry in a Result, encapsulating the entity and its associated data.
    
    Attributes:
        entity (Entity): The entity of the result entry.
            This is an instance of the Entity class, which represents a unique entity in the system.
            It contains information such as the entity's ID and type.
        stored_object (dict[str, Any]): The stored object of the result entry.
            This is essentially the raw data that was input into the system.

    ### Class variables

    `entity: superlinked.framework.storage.entity.Entity`
    :

    `stored_object: dict[str, typing.Any]`
    :