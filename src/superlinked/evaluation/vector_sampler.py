# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, cast

import numpy as np
from numpy import typing as npt

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema import T
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import InMemoryApp
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.storage.entity import Entity, EntityId


class VectorNotFoundError(Exception):
    pass


class VectorCollection:
    """
    Dataclass containing ids in a list, and vectors in a np.array. It is always true that `self.id_list[i]` is the id of
    the object of which `self.vectors[i]` is the embedded vector.

    Attributes:
        id_list (list[str]): List of object ids.
        vectors (npt.NDArray[np.float64]): Numpy array of
    """

    def __init__(self, id_list: list[str], vectors: npt.NDArray[np.float64]) -> None:
        if (len(id_list) > 1) & (len(id_list) != vectors.shape[0]):
            raise ValueError(
                f"id_list length and vectors parameter shape's first dimension should match. "
                f"Got {id_list=} and {vectors.shape[0]=}"
            )
        self.id_list: list[str] = id_list
        self.vectors: npt.NDArray[np.float64] = vectors

    def __len__(self) -> int:
        return len(self.id_list)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, VectorCollection):
            return (self.id_list == other.id_list) & np.allclose(
                self.vectors, other.vectors
            )
        return False

    def __str__(self) -> str:
        num_vectors: int = len(self.id_list)
        return f"VectorCollection of {num_vectors} vector{'s.' if num_vectors > 1 else '.'}"

    def __repr__(self) -> str:
        return self.__str__()


class VectorSampler:
    """
    VectorSampler is a class that provides methods to retrieve vectors from an App instance.
    It's important to note that this is intended for use exclusively with InMemoryStorage.

    Attributes:
        __app: An instance of InMemoryApp.

    Methods:
        __init__(self, app: InMemoryApp): Initializes a new instance of the VectorSampler class.

        get_vector_by_id(self, id_: str, index: Index, schema: IdSchemaObject | T) -> ndarray:
            Retrieves the vector of an entity by its id, schema, and the index it's stored in.
            If no entity is found, a VectorNotFoundError is raised.

        get_all_vectors(self, index: Index, schema: IdSchemaObject | T) -> ndarray:
            Retrieves all vectors for each entity in a given schema and the index it's stored in.
            If no entities are found, a VectorNotFoundError is raised.
    """

    def __init__(self, app: InMemoryApp) -> None:
        """
        Initializes a new instance of the VectorSampler class.

        Args:
            app (InMemoryApp): An instance of InMemoryApp.
        """
        self.__app = app

    def get_vectors_by_ids(
        self,
        id_: str | list[str],
        index: Index,
        schema: IdSchemaObject | T,
        readable_id_: str | list[str] | None = None,
    ) -> VectorCollection:
        """
        Retrieves an entity's vector by its id, schema, and the index it's stored in.

        Args:
            id_ (str) | list(str): The id of the entity(ies).
            index (Index): The index in which the entity is stored.
            schema (IdSchemaObject | T): The schema of the entity.
            readable_id_ (str) | list(str): The readable id of the entity(ies). For chunks, it is constructed from the
                origin_id (entity from which it originates from) and the chunk id. Defaults to using the ids.

        Returns:
            ndarray: The vector corresponding to the given id, index, and schema.

        Raises:
            VectorNotFoundError: If no entity is found.
        """
        schema = cast(IdSchemaObject, schema)
        ids = [id_] if isinstance(id_, str) else id_
        if readable_id_ is None:
            readable_ids = ids
        else:
            readable_ids = (
                [readable_id_] if isinstance(readable_id_, str) else readable_id_
            )
        if len(ids) != len(readable_ids):
            raise ValueError(
                f"id_ and readable_id_ should have the same length. "
                f"Got {len(ids)} and {len(readable_ids)}"
            )

        entity_vectors: list[npt.NDArray[np.float64]] = []
        entity_ids: list[str] = []
        for identification, readable_id in zip(ids, readable_ids):
            user_entity_id = EntityId(
                identification, index._node.node_id, schema._base_class_name
            )
            vector = self.__app.entity_store_manager.get_vector(user_entity_id)
            if vector is None:
                raise VectorNotFoundError(
                    f"No vector found for entity id {user_entity_id} in the given index and schema."
                )

            entity_vectors.append(vector.value)
            entity_ids.append(readable_id)

        return VectorCollection(entity_ids, np.array(entity_vectors))

    def get_all_vectors(
        self, index: Index, schema: IdSchemaObject | T, include_chunks: bool = False
    ) -> VectorCollection:
        """
        Retrieves all entities and their vectors for a given schema and the index they're stored in.

        Args:
            index (Index): The index in which the entities are stored.
            schema (IdSchemaObject | T): The schema of the entities.
            include_chunks (bool): Whether to include vectors of chunks present in the index. Chunks are created if
                the index contains a TextSimilaritySpace that is chunked.

        Returns:
            VectorCollection: All vectors for each corresponding entity to the given index and schema and a list of
                ids. Position `i` in the id list correspond to row `i` in the vector array.

        Raises:
            VectorNotFoundError: If no vector is found for any entities.
        """
        schema = cast(IdSchemaObject, schema)
        entities = self.__app.entity_store_manager.get_entities(
            index._node.node_id, schema._schema_name
        )
        if include_chunks:
            entity_ids: list[str] = [entity.id_.object_id for entity in entities]
            readable_ids: list[str] = [
                self.human_readable_id_for_chunks(entity) for entity in entities
            ]
            return self.get_vectors_by_ids(entity_ids, index, schema, readable_ids)

        entity_ids = list(
            {
                self.get_id_for_standalone_entity_origin_id_for_chunk(entity)
                for entity in entities
            }
        )
        return self.get_vectors_by_ids(entity_ids, index, schema)

    @staticmethod
    def get_id_for_standalone_entity_origin_id_for_chunk(entity: Entity) -> str:
        if entity.is_chunk():
            origin_id = cast(EntityId, entity.origin_id)
            return origin_id.object_id
        return entity.id_.object_id

    @staticmethod
    def human_readable_id_for_chunks(entity: Entity) -> str:
        if entity.is_chunk():
            origin_id = cast(EntityId, entity.origin_id)
            return f"{origin_id.object_id}-{entity.id_.object_id}"
        return entity.id_.object_id

    def __str__(self) -> str:
        return f"VectorSampler on app: {print(self.__app)}"

    def __repr__(self) -> str:
        return self.__str__()
