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

from collections import defaultdict
from dataclasses import dataclass

from beartype.typing import Any, Mapping, Sequence, TypeVar, cast

from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.data_types import NodeDataTypes, PythonTypes, Vector
from superlinked.framework.common.delayed_evaluator import DelayedEvaluator
from superlinked.framework.common.exception import (
    InvalidInputException,
    NotImplementedException,
)
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaField,
)
from superlinked.framework.common.settings import settings
from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import (
    FieldData,
    VectorFieldData,
)
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.field_type_converter import (
    FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE,
)
from superlinked.framework.common.storage.index_config import IndexConfig
from superlinked.framework.common.storage.query.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.common.storage_manager.entity_builder import EntityBuilder
from superlinked.framework.common.storage_manager.entity_data_request import (
    EntityDataRequest,
    NodeDataRequest,
    NodeRequest,
    NodeResultRequest,
)
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.node_info import NodeInfo
from superlinked.framework.common.storage_manager.node_result_data import NodeResultData
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming
from superlinked.framework.common.util.async_util import AsyncUtil
from superlinked.framework.dsl.query.query_user_config import QueryUserConfig

ResultTypeT = TypeVar("ResultTypeT")
NodeDataValueT = TypeVar("NodeDataValueT", bound=PythonTypes)


@dataclass
class SearchIndexParams:
    node_id: str
    length: int
    indexed_fields: Sequence[SchemaField]


class StorageManager:
    def __init__(
        self,
        vdb_connector: VDBConnector,
    ) -> None:
        self._vdb_connector = vdb_connector
        self._entity_builder = EntityBuilder()
        self._delayed_read_evaluator = DelayedEvaluator(
            settings.BATCHED_VDB_READ_WAIT_TIME_MS, self._vdb_connector.read_entities
        )
        self._delayed_write_evaluator = DelayedEvaluator(
            settings.BATCHED_VDB_WRITE_WAIT_TIME_MS,
            self._vdb_connector.write_entities,  # type: ignore
        )

    async def close_connection(self) -> None:
        await self._vdb_connector.close_connection()

    def init_search_indices(
        self,
        params_list: Sequence[SearchIndexParams],
        create_search_indices: bool,
        override_existing: bool = False,
    ) -> None:
        self._vdb_connector.init_search_index_configs(
            [self._compile_create_search_index_params(params) for params in params_list],
            create_search_indices,
            override_existing,
        )

    def _compile_create_search_index_params(self, params: SearchIndexParams) -> IndexConfig:
        vector_index_field_descriptor, index_field_descriptors = self._compile_indexed_fields_to_descriptors(params)
        return IndexConfig(
            StorageNaming.get_index_name_from_node_id(params.node_id),
            vector_index_field_descriptor,
            index_field_descriptors,
        )

    def _compile_indexed_fields_to_descriptors(
        self, params: SearchIndexParams
    ) -> tuple[VectorIndexFieldDescriptor, Sequence[IndexFieldDescriptor]]:
        vector_index_field_descriptor = VectorIndexFieldDescriptor(
            params.node_id,
            params.length,
            self._vdb_connector.distance_metric,
            self._vdb_connector.search_algorithm,
            self._vdb_connector.vector_precision,
        )

        return (
            vector_index_field_descriptor,
            list(self._create_index_field_descriptors_from_schema_fields(params.indexed_fields))
            + [
                IndexFieldDescriptor(field_descriptor.field.data_type, field_descriptor.field.name)
                for field_descriptor in self._entity_builder._admin_fields.field_descriptors
                if field_descriptor.should_be_returned
            ],
        )

    def _create_index_field_descriptors_from_schema_fields(
        self, schema_fields: Sequence[SchemaField]
    ) -> Sequence[IndexFieldDescriptor]:
        if unsupported_schema_field_indexing := [
            f"{schema_field.name} - {type(schema_field)}"
            for schema_field in schema_fields
            if not isinstance(schema_field, tuple(FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE.keys()))
        ]:
            raise NotImplementedException("Unindexable schema fields.", schema_fields=unsupported_schema_field_indexing)
        return [
            IndexFieldDescriptor(
                self._get_index_field_type_of_schema_field(cast(ConcreteSchemaField, schema_field)),
                StorageNaming.generate_field_name_from_schema_field(schema_field),
            )
            for schema_field in schema_fields
        ]

    def _get_index_field_type_of_schema_field(self, schema_field: ConcreteSchemaField) -> FieldDataType:
        return FIELD_DATA_TYPE_BY_SCHEMA_FIELD_TYPE[type(schema_field)]

    async def knn_search(
        self,
        index_node: IndexNode,
        schema: IdSchemaObject,
        knn_search_params: KNNSearchParams,
        query_user_config: QueryUserConfig,
        should_return_index_vector: bool = False,
        **params: Any,
    ) -> Sequence[SearchResultItem]:
        self._validate_knn_search_input(schema, knn_search_params.schema_fields_to_return)
        index_name = StorageNaming.get_index_name_from_node_id(index_node.node_id)
        vector_field = cast(
            VectorFieldData,
            self._entity_builder.compose_field_data(index_node.node_id, knn_search_params.vector),
        )
        schema_fields_by_fields = self._map_schema_fields_to_fields(knn_search_params.schema_fields_to_return)
        fields_to_return = list(schema_fields_by_fields.keys()) + list(self._entity_builder._admin_fields.header_fields)
        if should_return_index_vector:
            fields_to_return.append(self._entity_builder.compose_field(index_node.node_id, Vector))
        search_config = self._vdb_connector.init_search_config(query_user_config)
        search_result: Sequence[ResultEntityData] = await self._vdb_connector.knn_search(
            index_name,
            schema._schema_name,
            VDBKNNSearchParams(
                vector_field,
                knn_search_params.limit,
                fields_to_return,
                self._compose_filter_field_data(schema, knn_search_params.filters),
                knn_search_params.radius,
            ),
            search_config,
            **params,
        )
        schema_field_by_field_name = self._create_schema_field_by_field_name(schema_fields_by_fields)
        return [
            self._map_vdb_result_item_to_search_result_item(
                result_entity_data, schema_field_by_field_name, index_node.node_id
            )
            for result_entity_data in search_result
        ]

    def _create_schema_field_by_field_name(self, fields: dict[Field, SchemaField]) -> dict[str, SchemaField]:
        return {field.name: schema_field for field, schema_field in fields.items()}

    def _validate_knn_search_input(
        self,
        schema: IdSchemaObject,
        returned_schema_fields: Sequence[SchemaField] | None,
    ) -> None:
        if not returned_schema_fields:
            return
        if invalid_schema_fields := [
            schema_field for schema_field in returned_schema_fields if schema_field.schema_obj != schema
        ]:
            raise InvalidInputException(
                "`knn_search` can only return schema_fields from "
                + f"the searched schema {schema}, got {invalid_schema_fields}"
            )

    def _map_schema_fields_to_fields(self, returned_schema_fields: Sequence[SchemaField]) -> dict[Field, SchemaField]:
        return {
            self._entity_builder.convert_schema_field_to_field(returned_schema_field): returned_schema_field
            for returned_schema_field in returned_schema_fields
        }

    def _compose_filter_field_data(
        self, schema: IdSchemaObject, filters: Sequence[ComparisonOperation[SchemaField]]
    ) -> Sequence[ComparisonOperation[Field]]:
        return [
            ComparisonOperation(
                filter_._op,
                cast(
                    ComparisonOperand,
                    self._entity_builder.convert_schema_field_to_field(cast(SchemaField, filter_._operand)),
                ),
                filter_._other,
                filter_._group_key,
            )
            for filter_ in filters
        ] + [self._entity_builder._admin_fields.schema_id.field == schema._schema_name]

    def _map_vdb_result_item_to_search_result_item(
        self,
        result_entity_data: ResultEntityData,
        schema_field_by_field_name: Mapping[str, SchemaField],
        index_node_id: str,
    ) -> SearchResultItem:
        parsed_schema_fields = [
            self._entity_builder.parse_schema_field_data(field_data, schema_field_by_field_name)
            for field_data in result_entity_data.field_data.values()
            if not self._entity_builder._admin_fields.is_admin_field(field_data)
            and field_data.name in schema_field_by_field_name
        ]
        index_vector: Vector | None = None
        if index_vector_field := next(
            (
                field_data
                for field_name, field_data in result_entity_data.field_data.items()
                if field_name == index_node_id
            ),
            None,
        ):
            index_vector = cast(Vector, index_vector_field.value)
        return SearchResultItem(
            self._entity_builder._admin_fields.extract_header(result_entity_data.field_data),
            parsed_schema_fields,
            result_entity_data.score,
            index_vector,
        )

    async def write_combined_ingestion_result(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        cached_items: Mapping[EntityId, Mapping[str, NodeInfo]],
        entity_to_origin_id: Mapping[EntityId, str],
        fields_to_exclude: Sequence[SchemaField],
    ) -> None:
        entity_data_items = [
            self._entity_builder.compose_entity_data_from_parsed_schema(parsed_schema, fields_to_exclude)
            for parsed_schema in parsed_schemas
        ]
        cached_entity_data = [
            self._entity_builder.compose_entity_data_from_node_info_items(
                entity_id, entity_to_origin_id.get(entity_id), node_id_to_node_info
            )
            for entity_id, node_id_to_node_info in cached_items.items()
        ]
        entity_data_items.extend(cached_entity_data)
        await self._delayed_write_evaluator.evaluate(entity_data_items)

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def write_parsed_schema_fields(
        self, parsed_schemas: Sequence[ParsedSchema], fields_to_exclude: Sequence[SchemaField]
    ) -> None:
        entities_to_write = [
            self._entity_builder.compose_entity_data_from_parsed_schema(parsed_schema, fields_to_exclude)
            for parsed_schema in parsed_schemas
        ]
        AsyncUtil.run(self._delayed_write_evaluator.evaluate(entities_to_write))

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def write_node_results(self, node_data_items: Sequence[NodeResultData]) -> None:
        entities_to_write = [
            self._entity_builder.compose_entity_data_from_node_result(node_data) for node_data in node_data_items
        ]
        AsyncUtil.run(self._delayed_write_evaluator.evaluate(entities_to_write))

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def write_node_data(
        self, schema: IdSchemaObject, node_data_by_object_id: Mapping[str, dict[str, PythonTypes]], node_id: str
    ) -> None:
        entity_data_items = [
            self._compose_entity_data(schema, object_id, node_id, node_data)
            for object_id, node_data in node_data_by_object_id.items()
        ]
        AsyncUtil.run(self._delayed_write_evaluator.evaluate(entity_data_items))

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def _compose_entity_data(
        self, schema: IdSchemaObject, object_id: str, node_id: str, node_data: dict[str, PythonTypes]
    ) -> EntityData:
        entity_id = self._entity_builder.compose_entity_id(schema._schema_name, object_id)
        field_data = list(self._entity_builder._admin_fields.create_header_field_data(entity_id))
        field_data.extend(list(self._entity_builder.compose_field_data_from_node_data(node_id, node_data)))
        return EntityData(entity_id, {fd.name: fd for fd in field_data})

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def read_node_results(
        self,
        schemas_with_object_ids: Sequence[tuple[IdSchemaObject, str]],
        node_id: str,
        result_type: type[ResultTypeT],
    ) -> list[ResultTypeT | None]:
        return AsyncUtil.run(self.read_node_results_async(schemas_with_object_ids, node_id, result_type))

    # TODO FAB-3639 - legacy-readwrite-interfaces
    async def read_node_results_async(
        self,
        schemas_with_object_ids: Sequence[tuple[IdSchemaObject, str]],
        node_id: str,
        result_type: type[ResultTypeT],
    ) -> list[ResultTypeT | None]:
        entity_ids = [
            self._entity_builder.compose_entity_id(schema._schema_name, object_id)
            for schema, object_id in schemas_with_object_ids
        ]
        result_field = self._entity_builder.compose_field(node_id, result_type)
        entities = [self._entity_builder.compose_entity(entity_id, [result_field]) for entity_id in entity_ids]
        entity_data = await self._delayed_read_evaluator.evaluate(entities)

        def cast_value_if_not_none(field_data: FieldData | None) -> ResultTypeT | None:
            return cast(ResultTypeT, field_data.value) if field_data is not None else None

        return [cast_value_if_not_none(ed.field_data.get(result_field.name)) for ed in entity_data]

    # TODO FAB-3639 - legacy-readwrite-interfaces
    async def read_node_result(
        self,
        schema: IdSchemaObject,
        object_id: str,
        node_id: str,
        result_type: type[ResultTypeT],
    ) -> ResultTypeT | None:
        return next(iter(await self.read_node_results_async([(schema, object_id)], node_id, result_type)))

    async def read_entity_data_requests(
        self, entity_data_requests: Sequence[EntityDataRequest]
    ) -> list[dict[str, NodeInfo]]:
        entities, node_requests_to_fields = zip(
            *[self._create_entity_and_node_request_to_field(request) for request in entity_data_requests]
        )
        entity_data = await self._delayed_read_evaluator.evaluate(entities)
        return [
            self._create_node_id_to_node_info(node_request_to_field, ed.field_data)
            for node_request_to_field, ed in zip(node_requests_to_fields, entity_data)
        ]

    def _create_entity_and_node_request_to_field(
        self, request: EntityDataRequest
    ) -> tuple[Entity, dict[NodeRequest, Field]]:
        request_to_field = {
            node_request: node_request.to_field(self._entity_builder) for node_request in request.node_requests
        }
        entities = self._entity_builder.compose_entity(request.entity_id, list(request_to_field.values()))
        return entities, request_to_field

    def _create_node_id_to_node_info(
        self, node_request_to_field: Mapping[NodeRequest, Field], field_data: Mapping[str, FieldData]
    ) -> dict[str, NodeInfo]:
        node_result = {
            node_request.node_id: field_data[field.name].value if field.name in field_data else None
            for node_request, field in node_request_to_field.items()
            if isinstance(node_request, NodeResultRequest)
        }

        node_data: dict[str, dict[str, NodeDataTypes]] = defaultdict(dict)
        for node_request, field in node_request_to_field.items():
            if isinstance(node_request, NodeDataRequest) and field.name in field_data:
                node_data[node_request.node_id].update({node_request.field_name: field_data[field.name].value})

        node_ids = set(node_result.keys()).union(node_data.keys())
        return {node_id: NodeInfo(node_result.get(node_id, None), node_data.get(node_id, {})) for node_id in node_ids}

    # TODO FAB-3639 - legacy-readwrite-interfaces
    # TODO FAI-2737 to solve the parameters
    def read_node_data(
        self,
        schema: IdSchemaObject,
        object_ids: Sequence[str],
        node_id: str,
        node_data_descriptor: dict[str, type[NodeDataValueT]],
    ) -> dict[str, dict[str, NodeDataValueT]]:
        field_by_node_data_key = self._map_fields_by_node_data_keys(node_id, node_data_descriptor or {})
        if not field_by_node_data_key:
            return {object_id: {} for object_id in object_ids}
        node_data_key_by_field_name = {field.name: key for key, field in field_by_node_data_key.items()}
        fields = list(field_by_node_data_key.values())
        entities = [self._compose_entity(schema, object_id, fields) for object_id in object_ids]
        entity_data_items = AsyncUtil.run(self._delayed_read_evaluator.evaluate(entities))
        node_data_items = {
            object_id: {
                node_data_key_by_field_name[field_data.name]: cast(NodeDataValueT, field_data.value)
                for field_data in entity_data.field_data.values()
            }
            for object_id, entity_data in zip(object_ids, entity_data_items)
        }
        return node_data_items

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def _map_fields_by_node_data_keys(
        self, node_id: str, node_data_descriptor: dict[str, type[NodeDataValueT]]
    ) -> dict[str, Field]:
        return {
            key: self._entity_builder.compose_field_from_node_data_descriptor(
                node_id, key, cast(type[PythonTypes], type_)
            )
            for key, type_ in node_data_descriptor.items()
        }

    # TODO FAB-3639 - legacy-readwrite-interfaces
    def _compose_entity(self, schema: IdSchemaObject, object_id: str, fields: Sequence[Field]) -> Entity:
        entity_id = self._entity_builder.compose_entity_id(schema._schema_name, object_id)
        entity = self._entity_builder.compose_entity(entity_id, fields)
        return entity
