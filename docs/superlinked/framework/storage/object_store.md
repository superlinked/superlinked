Module superlinked.framework.storage.object_store
=================================================

Classes
-------

`ObjectStore()`
:   Interface for class that can store and retrieve
    objects by id.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.storage.in_memory_object_store.InMemoryObjectStore

    ### Methods

    `load(self, row_id: str) ‑> Optional[~ObjectTypeT]`
    :

    `load_all(self) ‑> list[~ObjectTypeT]`
    :

    `save(self, row_id: str, data: ObjectTypeT) ‑> None`
    :