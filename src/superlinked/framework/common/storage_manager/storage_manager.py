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

from itertools import groupby
from typing import Any, Iterator, TypeVar, cast

from beartype.typing import Sequence

from superlinked.framework.common.calculation.distance_metric import DistanceMetric
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.data_types import Json, PythonTypes
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField, SchemaObject
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import VectorFieldData
from superlinked.framework.common.storage.result_entity_data import ResultEntityData
from superlinked.framework.common.storage.search_index_creation.index_field_descriptor import (
    IndexFieldDescriptor,
    VectorIndexFieldDescriptor,
)
from superlinked.framework.common.storage.search_index_creation.search_algorithm import (
    SearchAlgorithm,
)
from superlinked.framework.common.storage.search_index_creation.vector_component_precision import (
    VectorComponentPrecision,
)
from superlinked.framework.common.storage.vdb_connector import VDBConnector
from superlinked.framework.common.storage.vdb_knn_search_params import (
    VDBKNNSearchParams,
)
from superlinked.framework.common.storage_manager.entity_builder import EntityBuilder
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming

ResultTypeT = TypeVar("ResultTypeT")
# NodeDataValueType
NDVT = TypeVar("NDVT", bound=PythonTypes)


class StorageManager:
    def __init__(
        self,
        vdb_connector: VDBConnector,
    ) -> None:
        self._vdb_connector = vdb_connector
        self._storage_naming = StorageNaming()
        self._entity_builder = EntityBuilder(self._storage_naming)

    def close_connection(self) -> None:
        self._vdb_connector.close_connection()

    def create_search_index(
        self,
        dag: Dag,
        distance_metric: DistanceMetric = DistanceMetric.INNER_PRODUCT,
        search_algorithm: SearchAlgorithm = SearchAlgorithm.FLAT,
        vector_coordinate_type: VectorComponentPrecision = VectorComponentPrecision.FLOAT32,
    ) -> None:
        vector_index_field_descriptor, index_field_descriptors = (
            self._get_index_field_descriptors_from_dag(
                dag,
                distance_metric,
                search_algorithm,
                vector_coordinate_type,
            )
        )
        self._vdb_connector.create_search_index(
            self._storage_naming.get_index_name_from_index_node(dag.index_node),
            vector_index_field_descriptor,
            index_field_descriptors,
        )

    def drop_search_index(self, index_node: IndexNode) -> None:
        index_name = self._storage_naming.get_index_name_from_index_node(index_node)
        self._vdb_connector.drop_search_index(index_name)

    def knn_search(
        self,
        index_node: IndexNode,
        schema: IdSchemaObject,
        returned_schema_fields: Sequence[SchemaField],
        knn_search_params: KNNSearchParams,
        **params: Any,
    ) -> Sequence[SearchResultItem]:
        self._validate_knn_search_input(schema, returned_schema_fields)
        index_name = self._storage_naming.get_index_name_from_index_node(index_node)
        vector_field = cast(
            VectorFieldData,
            self._entity_builder.compose_field_data(
                index_node.node_id, knn_search_params.vector
            ),
        )
        returned_fields = {
            self._entity_builder.convert_schema_field_to_field(
                returned_schema_field
            ): returned_schema_field
            for returned_schema_field in returned_schema_fields
        }
        search_result: Sequence[ResultEntityData] = self._vdb_connector.knn_search(
            index_name,
            schema._schema_name,
            list(returned_fields.keys())
            + list(self._entity_builder._admin_fields.header_fields),
            VDBKNNSearchParams(
                vector_field,
                knn_search_params.limit,
                self._compose_filter_field_data(
                    schema, knn_search_params.filters or []
                ),
                knn_search_params.radius,
            ),
            **params,
        )
        schema_field_by_field_name = self._create_schema_field_by_field_name(
            returned_fields
        )
        return [
            SearchResultItem(
                self._entity_builder._admin_fields.extract_header(
                    result_entity_data.field_data
                ),
                [
                    self._entity_builder.parse_schema_field_data(
                        field_data, schema_field_by_field_name
                    )
                    for field_data in result_entity_data.field_data.values()
                    if not self._entity_builder._admin_fields.is_admin_field(field_data)
                ],
                result_entity_data.score,
            )
            for result_entity_data in search_result
        ]

    def _validate_knn_search_input(
        self,
        schema: SchemaObject,
        returned_schema_fields: Sequence[SchemaField],
    ) -> None:
        if invalid_schema_fields := [
            schema_field
            for schema_field in returned_schema_fields
            if schema_field.schema_obj != schema
        ]:
            raise InvalidSchemaException(
                "`knn_search` can only return schema_fields from "
                + f"the searched schema {schema}, got {invalid_schema_fields}"
            )

    def _compose_filter_field_data(
        self, schema: SchemaObject, filters: Sequence[ComparisonOperation[SchemaField]]
    ) -> Sequence[ComparisonOperation[Field]]:
        return [
            ComparisonOperation(
                filter_._op,
                self._entity_builder.convert_schema_field_to_field(
                    cast(SchemaField, filter_._operand)
                ),
                filter_._other,
            )
            for filter_ in filters
        ] + [self._entity_builder._admin_fields.schema_id.field == schema._schema_name]

    def write_object_blob(
        self, schema: SchemaObject, object_id: str, object_blob: Json
    ) -> None:
        if object_blob_data_field := (
            self._entity_builder._admin_fields.create_object_blob_field_data(
                object_blob
            )
        ):
            entity_data = self._entity_builder.compose_entity_data(
                schema._schema_name,
                object_id,
                [object_blob_data_field],
            )
            self._vdb_connector.write_entities([entity_data])

    def write_parsed_schema_fields(
        self, object_id: str, parsed_schema_fields: Sequence[ParsedSchemaField]
    ) -> None:
        def get_schema_name_of_parsed_schema_field(
            parsed_schema_field: ParsedSchemaField,
        ) -> str:
            return parsed_schema_field.schema_field.schema_obj._schema_name

        def group_parsed_schema_fields_by_schema_name(
            parsed_schema_fields: Sequence[ParsedSchemaField],
        ) -> Iterator[tuple[str, Iterator[ParsedSchemaField]]]:
            return groupby(
                sorted(
                    parsed_schema_fields,
                    key=get_schema_name_of_parsed_schema_field,
                ),
                get_schema_name_of_parsed_schema_field,
            )

        entity_data = [
            self._entity_builder.compose_entity_data_from_parsed_schema_fields(
                schema_name, object_id, list(parsed_schema_fields_group)
            )
            for schema_name, parsed_schema_fields_group in group_parsed_schema_fields_by_schema_name(
                parsed_schema_fields
            )
        ]
        self._vdb_connector.write_entities(entity_data)

    def write_node_result(
        self,
        schema: SchemaObject,
        object_id: str,
        node_id: str,
        result: PythonTypes,
        origin_id: str | None = None,
    ) -> None:
        entity_id = self._entity_builder.compose_entity_id(
            schema._schema_name, object_id
        )
        field_data = list(
            self._entity_builder._admin_fields.create_header_field_data(
                entity_id, origin_id
            )
        )
        if result is not None:
            result_field_data = self._entity_builder.compose_field_data(node_id, result)
            field_data.append(result_field_data)
        self._vdb_connector.write_entities(
            [EntityData(entity_id, {fd.name: fd for fd in field_data})]
        )

    def write_node_data(
        self,
        schema: SchemaObject,
        object_id: str,
        node_id: str,
        node_data: dict[str, PythonTypes],
    ) -> None:
        entity_id = self._entity_builder.compose_entity_id(
            schema._schema_name, object_id
        )
        field_data = list(
            self._entity_builder._admin_fields.create_header_field_data(entity_id)
        )
        field_data.extend(
            list(
                self._entity_builder.compose_field_data_from_node_data(
                    node_id, node_data
                )
            )
        )
        self._vdb_connector.write_entities(
            [EntityData(entity_id, {fd.name: fd for fd in field_data})]
        )

    def read_object_blob(
        self, schema: SchemaObject, object_id: str
    ) -> dict[str, Any] | None:
        entity = self._entity_builder.compose_entity(
            self._entity_builder.compose_entity_id(schema._schema_name, object_id),
            [self._entity_builder._admin_fields.object_blob.field],
        )
        entity_data = self._vdb_connector.read_entities([entity])
        if not entity_data:
            return None
        return self._entity_builder._admin_fields.extract_object_blob_field_data(
            entity_data[0].field_data
        )

    def read_schema_field_values(
        self, object_id: str, schema_fields: Sequence[SchemaField]
    ) -> ParsedSchema:
        schema = self._get_schema_of_schema_fields(schema_fields)
        entity_id = self._entity_builder.compose_entity_id(
            schema._schema_name, object_id
        )
        fields = {
            self._entity_builder.convert_schema_field_to_field(
                schema_field
            ): schema_field
            for schema_field in schema_fields
        }
        entity = self._entity_builder.compose_entity(entity_id, list(fields.keys()))
        entity_data = self._vdb_connector.read_entities([entity])[0]

        schema_field_by_field_name = self._create_schema_field_by_field_name(fields)
        return self._entity_builder.parse_entity_data(
            schema, entity_data, schema_field_by_field_name
        )

    def _get_schema_of_schema_fields(
        self,
        schema_fields: Sequence[SchemaField],
    ) -> IdSchemaObject:
        schemas = {schema_field.schema_obj for schema_field in schema_fields}
        if len(schemas) != 1:
            raise InvalidSchemaException(
                f"`schema_fields` must have the same root schema, got {schemas}"
            )
        schema = schemas.pop()
        if not isinstance(schema, IdSchemaObject):
            raise InvalidSchemaException(
                f"The root schema of `schema_fields` must be an {IdSchemaObject.__name__}"
            )
        return schema

    def read_node_result(
        self,
        schema: SchemaObject,
        object_id: str,
        node_id: str,
        result_type: type[ResultTypeT],
    ) -> ResultTypeT | None:
        entity_id = self._entity_builder.compose_entity_id(
            schema._schema_name, object_id
        )
        result_field = self._entity_builder.compose_field(node_id, result_type)
        fields = [result_field]
        entity = self._entity_builder.compose_entity(entity_id, fields)
        entity_data = self._vdb_connector.read_entities([entity])[0]
        result_value = next(
            (
                cast(ResultTypeT, field_data.value)
                for field_data in entity_data.field_data.values()
                if field_data.name == result_field.name
            ),
            None,
        )
        return result_value

    def read_node_data(
        self,
        schema: SchemaObject,
        object_id: str,
        node_id: str,
        node_data_descriptor: dict[str, type[NDVT]],
    ) -> dict[str, NDVT]:
        entity_id = self._entity_builder.compose_entity_id(
            schema._schema_name, object_id
        )
        field_by_node_data_key = self._map_fields_by_node_data_keys(
            node_id, node_data_descriptor or {}
        )
        if not field_by_node_data_key:
            return {}
        fields = list(field_by_node_data_key.values())
        node_data_key_by_field_name = {
            field.name: key for key, field in field_by_node_data_key.items()
        }
        entity = self._entity_builder.compose_entity(entity_id, fields)
        entity_data = self._vdb_connector.read_entities([entity])[0]
        node_data = {
            node_data_key_by_field_name[field_data.name]: cast(NDVT, field_data.value)
            for field_data in entity_data.field_data.values()
        }
        return node_data

    def _get_index_field_descriptors_from_dag(
        self,
        dag: Dag,
        distance_metric: DistanceMetric,
        search_algorithm: SearchAlgorithm,
        vector_coordinate_type: VectorComponentPrecision,
    ) -> tuple[VectorIndexFieldDescriptor, Sequence[IndexFieldDescriptor]]:
        index_node = dag.index_node
        vector_index_field_descriptor = VectorIndexFieldDescriptor(
            index_node.node_id,
            index_node.length,
            distance_metric,
            search_algorithm,
            vector_coordinate_type,
        )
        indexed_fields = StorageManager._get_indexed_schema_fields_of_dag(dag)

        return (
            vector_index_field_descriptor,
            [
                IndexFieldDescriptor(
                    self._storage_naming.generate_field_name_from_schema_field(
                        indexed_field
                    )
                )
                for indexed_field in indexed_fields
            ]
            + [
                IndexFieldDescriptor(
                    self._entity_builder._admin_fields.schema_id.field.name
                )
            ],
        )

    def _create_schema_field_by_field_name(
        self, fields: dict[Field, SchemaField]
    ) -> dict[str, SchemaField]:
        return {field.name: schema_field for field, schema_field in fields.items()}

    def _map_fields_by_node_data_keys(
        self, node_id: str, node_data_descriptor: dict[str, type[NDVT]]
    ) -> dict[str, Field]:
        return {
            key: self._entity_builder.compose_field_from_node_data_descriptor(
                node_id, key, cast(type[PythonTypes], type_)
            )
            for key, type_ in node_data_descriptor.items()
        }

    @staticmethod
    def _get_indexed_schema_fields_of_dag(dag: Dag) -> Sequence[SchemaField]:
        # TODO FAI-1814: this should be filtered by the soon-to-be introduced Indexed property of the SchemaField.
        return [
            schema_field
            for schema in dag.schemas
            for schema_field in schema._get_schema_fields()
        ]
