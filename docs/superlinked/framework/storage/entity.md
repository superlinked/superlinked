Module superlinked.framework.storage.entity
===========================================

Classes
-------

`Entity(id_: superlinked.framework.storage.entity.EntityId, items: Mapping[str, superlinked.framework.storage.field.Field], origin_id: superlinked.framework.storage.entity.EntityId | None, entity_metadata: superlinked.framework.storage.entity.EntityMetadata | None)`
:   Entity contains the stored field values of a schema,
    queries return the values in entities too.

    ### Methods

    `is_chunk(self) ‑> bool`
    :

`EntityId(object_id: str, node_id: str, schema_id: str)`
:   EntityId is used to identify a single entry within the vector storage.

    ### Class variables

    `node_id: str`
    :

    `object_id: str`
    :

    `schema_id: str`
    :

`EntityMetadata(similarity: float | None)`
:   EntityMetadata encompasses all possible metadata associated with an entity.

    ### Class variables

    `similarity: float | None`
    :