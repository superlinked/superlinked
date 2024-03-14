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

from dataclasses import dataclass
from typing import Any

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.storage.persistence_type import PersistenceType
from superlinked.framework.online.dag.evaluation_result import (
    ERT,
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.storage.entity import EntityId
from superlinked.framework.storage.entity_store_manager import EntityStoreManager


class EvaluationResultStoreManager:
    RESULT_KEY = "__evaluation_result__"
    RESULT_META_KEY = "__evaluation_result_meta__"

    @dataclass
    class SaveSingleResultArgs:
        entity_id: EntityId
        result: SingleEvaluationResult
        schema_name: str
        persistence_type: PersistenceType
        origin_id: EntityId | None = None

    @dataclass
    class SaveResultMetaArgs:
        main_object_id: str
        schema_name: str
        node_id: str
        key: str
        metadata: str

    def __init__(self, store_manager: EntityStoreManager) -> None:
        self.store_manager = store_manager

    def save_result(
        self,
        result: EvaluationResult[ERT],
        main_object_id: str,
        schema_name: str,
        persistence_type: PersistenceType,
    ) -> None:
        entity_id = EvaluationResultStoreManager._create_entity_id(
            main_object_id, result.main.node_id, schema_name
        )
        # Saving main
        self.save_single_result(
            EvaluationResultStoreManager.SaveSingleResultArgs(
                entity_id,
                result.main,
                schema_name,
                persistence_type,
            )
        )
        # Saving chunks
        self.save_chunks(result.chunks, schema_name, persistence_type, entity_id)

    def save_single_result(self, args: SaveSingleResultArgs) -> None:
        match args.persistence_type:
            case PersistenceType.VECTOR:
                if isinstance(args.result.value, Vector):
                    self.store_manager.set_vector(
                        args.entity_id,
                        args.result.value,
                        args.schema_name,
                        args.origin_id,
                    )
                else:
                    raise ValueError(
                        f"Cannot store data of type {type(args.result.value)} as a Vector."
                    )
            case PersistenceType.PROPERTY:
                self.store_manager.set_property(
                    args.entity_id,
                    EvaluationResultStoreManager.RESULT_KEY,
                    args.result.value,
                    args.origin_id,
                )

    def save_chunks(
        self,
        chunks: list[SingleEvaluationResult],
        schema_name: str,
        persistence_type: PersistenceType,
        origin_id: EntityId,
    ) -> None:
        for chunk in chunks:
            chunk_entity_id = EvaluationResultStoreManager._create_entity_id(
                chunk.object_id, chunk.node_id, schema_name
            )
            self.save_single_result(
                EvaluationResultStoreManager.SaveSingleResultArgs(
                    chunk_entity_id, chunk, schema_name, persistence_type, origin_id
                )
            )

    def save_result_meta(self, args: SaveResultMetaArgs) -> None:
        entity_id = EvaluationResultStoreManager._create_entity_id(
            args.main_object_id, args.node_id, args.schema_name
        )
        self.store_manager.set_property(
            entity_id,
            EvaluationResultStoreManager._get_metadata_property_key(args.key),
            args.metadata,
        )

    def load_single_result(
        self,
        main_object_id: str,
        node_id: str,
        schema_name: str,
        persistence_type: PersistenceType,
    ) -> SingleEvaluationResult | None:
        entity_id = EvaluationResultStoreManager._create_entity_id(
            main_object_id, node_id, schema_name
        )
        stored_result: Any
        match persistence_type:
            case PersistenceType.VECTOR:
                stored_result = self.store_manager.get_vector(entity_id)
            case PersistenceType.PROPERTY:
                stored_result = self.store_manager.get_property(
                    entity_id, EvaluationResultStoreManager.RESULT_KEY
                )
        if not stored_result:
            return None
        return SingleEvaluationResult(node_id, stored_result)

    def load_result_meta(
        self,
        main_object_id: str,
        schema_name: str,
        node_id: str,
        key: str,
    ) -> str | None:
        entity_id = EvaluationResultStoreManager._create_entity_id(
            main_object_id, node_id, schema_name
        )
        return self.store_manager.get_property(
            entity_id,
            EvaluationResultStoreManager._get_metadata_property_key(key),
        )

    @staticmethod
    def _create_entity_id(object_id: str, node_id: str, schema_name: str) -> EntityId:
        return EntityId(object_id, node_id, schema_name)

    @staticmethod
    def _get_metadata_property_key(key: str) -> str:
        return f"{EvaluationResultStoreManager.RESULT_META_KEY}:{key}"
