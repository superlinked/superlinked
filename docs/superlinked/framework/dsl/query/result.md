Module superlinked.framework.dsl.query.result
=============================================

Classes
-------

`Result(schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, entities: list[superlinked.framework.storage.entity.Entity])`
:   A class representing the result of a query.
    
    Attributes:
        schema (SchemaObject): The schema object.
        entities (list[Entity]): The list of entities (items) in order.
        The id of the entities refer to the original elements.
    
    Initialize the Result.
    
    Args:
        schema (SchemaObject): The schema object.
        entities (list[Entity]): The list of entities.