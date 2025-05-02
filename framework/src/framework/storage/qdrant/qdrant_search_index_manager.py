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


from beartype.typing import Sequence
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from typing_extensions import override

from superlinked.framework.common.storage.exception import (
    IndexConfigNotFoundException,
    InvalidIndexConfigException,
    MismatchingConfigException,
)
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.search_index.manager.search_index_manager import (
    SearchIndexManager,
)
from superlinked.framework.common.storage.search_index.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.storage.qdrant.qdrant_field_descriptor_compiler import (
    QdrantFieldDescriptorCompiler,
)


class QdrantSearchIndexManager(SearchIndexManager):
    def __init__(
        self,
        client: QdrantClient,
        index_configs: Sequence[IndexConfig] | None = None,
    ) -> None:
        super().__init__(index_configs)
        self._client = client

    @property
    @override
    def supported_vector_indexing(self) -> Sequence[SearchAlgorithm]:
        # SearchAlgorithm.FLAT is only supported query time by setting the
        # `exact` param to True.
        return [SearchAlgorithm.HNSW, SearchAlgorithm.FLAT]

    @override
    def _create_search_indices(
        self,
        index_configs: Sequence[IndexConfig],
        collection_name: str,
        override_existing: bool = False,
    ) -> None:
        self._validate_index_configs(index_configs)
        if override_existing:
            self._client.delete_collection(collection_name)

        vector_config = QdrantFieldDescriptorCompiler.create_vector_config(index_configs)
        if self._client.collection_exists(collection_name):
            self._check_mismatching_config(vector_config, collection_name)
        else:
            self._client.create_collection(collection_name=collection_name, vectors_config=vector_config)
        self._create_payload_indices(index_configs, collection_name)

    def _validate_index_configs(self, index_configs: Sequence[IndexConfig]) -> None:
        if not index_configs:
            raise IndexConfigNotFoundException("Qdrant without search indices isn't supported.")
        if invalid_search_algorithm_configs := [
            index_config
            for index_config in index_configs
            if index_config.vector_field_descriptor.search_algorithm not in self.supported_vector_indexing
        ]:
            raise InvalidIndexConfigException(
                f"Unsupported search algorithm found: {invalid_search_algorithm_configs}, "
                + f"{type(self)} only supports {self.supported_vector_indexing}."
            )

    def _check_mismatching_config(
        self,
        vector_config: dict[str, VectorParams],
        collection_name: str,
    ) -> None:
        existing_vector_config = self._client.get_collection(collection_name).config.params.vectors or {}
        if not isinstance(existing_vector_config, dict):
            raise InvalidIndexConfigException(
                f"Existing index config {existing_vector_config} doesn't support named vector indexing."
            )
        if invalid_params := {
            vector_name: {
                "existing": existing_vector_config.get(vector_name),
                "configured": vector_param,
            }
            for vector_name, vector_param in vector_config.items()
            if existing_vector_config.get(vector_name) != vector_param
        }:
            raise MismatchingConfigException(
                f"Collision found between existing and configured indices: {invalid_params}"
            )

    def _create_payload_indices(self, index_configs: Sequence[IndexConfig], collection_name: str) -> None:
        field_schema_by_field_name = QdrantFieldDescriptorCompiler.compile_payload_field_descriptors(index_configs)
        for field_name, field_schema in field_schema_by_field_name.items():
            self._client.create_payload_index(collection_name, field_name, field_schema)
