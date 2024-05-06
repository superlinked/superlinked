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


from typing import Any

from beartype.typing import Sequence

from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.storage.entity import Entity
from superlinked.framework.common.storage.entity_data import EntityData
from superlinked.framework.common.storage.entity_id import EntityId
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData, StringFieldData
from superlinked.framework.common.storage_manager.field_type_converter import (
    FieldTypeConverter,
)
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming


class EntityBuilder:
    def __init__(
        self,
        storage_naming: StorageNaming,
        field_type_converter: FieldTypeConverter | None = None,
    ) -> None:
        self._storage_naming = storage_naming
        self._field_type_converter = field_type_converter or FieldTypeConverter()

    def compose_entity_id(self, schema_id: str, object_id: str) -> EntityId:
        return EntityId(schema_id, object_id)

    def compose_entity(self, entity_id: EntityId, fields: Sequence[Field]) -> Entity:
        return Entity(entity_id, fields)

    def convert_schema_field_to_field(self, schema_field: SchemaField) -> Field:
        return Field(
            self._field_type_converter.convert_schema_field_type(type(schema_field)),
            self._storage_naming.generate_field_name_from_schema_field(schema_field),
        )

    def convert_parsed_schema_field_to_field_data(
        self, parsed_schema_field: ParsedSchemaField
    ) -> FieldData:
        field = self.convert_schema_field_to_field(parsed_schema_field.schema_field)
        return FieldData.from_field(field, parsed_schema_field.value)

    def compose_entity_from_schema_fields(
        self,
        schema_id: str,
        object_id: str,
        schema_fields: Sequence[SchemaField],
    ) -> Entity:
        entity_id = self.compose_entity_id(schema_id, object_id)
        return Entity(
            entity_id,
            [
                self.convert_schema_field_to_field(schema_field)
                for schema_field in schema_fields
            ],
        )

    def compose_entity_data(
        self,
        schema_id: str,
        object_id: str,
        parsed_schema_fields: Sequence[ParsedSchemaField],
    ) -> EntityData:
        entity_id = self.compose_entity_id(schema_id, object_id)
        base_fields = list(self.create_admin_field_data(entity_id))
        return EntityData(
            entity_id,
            [
                self.convert_parsed_schema_field_to_field_data(parsed_schema_field)
                for parsed_schema_field in parsed_schema_fields
            ]
            + base_fields,
        )

    def parse_schema_field_data(
        self,
        schema_field_data: FieldData,
        schema_field_by_field_name: dict[str, SchemaField],
    ) -> ParsedSchemaField:
        return ParsedSchemaField.from_schema_field(
            schema_field_by_field_name[schema_field_data.name], schema_field_data.value
        )

    def parse_entity_data(
        self,
        schema: IdSchemaObject,
        entity_data: EntityData,
        schema_field_by_field_name: dict[str, SchemaField],
    ) -> ParsedSchema:
        return ParsedSchema(
            schema,
            entity_data.id_.object_id,
            [
                self.parse_schema_field_data(field_data, schema_field_by_field_name)
                for field_data in entity_data.field_data
            ],
        )

    def create_admin_field_data(
        self,
        entity_id: EntityId,
        origin_id: str | None = None,
    ) -> Sequence[FieldData]:
        field_data = [
            StringFieldData(StorageNaming.SCHEMA_INDEX_NAME, entity_id.schema_id),
            StringFieldData(StorageNaming.OBJECT_ID_INDEX_NAME, entity_id.object_id),
        ]
        if origin_id:
            field_data.append(
                StringFieldData(StorageNaming.ORIGIN_ID_INDEX_NAME, origin_id)
            )
        return field_data

    def compose_field_from_node_data_descriptor(
        self, node_data_key: str, node_data_type: type
    ) -> Field:
        return Field(
            self._field_type_converter.convert_python_type(node_data_type),
            self._storage_naming.generate_node_data_field_name(node_data_key),
        )

    def compose_field(
        self,
        node_id: str,
        result_type: type,
    ) -> Field:
        return Field(
            self._field_type_converter.convert_python_type(result_type),
            node_id,
        )

    def compose_field_data(
        self,
        node_id: str,
        result: Any,
    ) -> FieldData:
        return FieldData(
            self._field_type_converter.convert_python_type(type(result)),
            node_id,
            result,
        )

    def compose_field_data_from_node_data(
        self, node_data: dict[str, Any]
    ) -> Sequence[FieldData]:
        return [
            FieldData(
                self._field_type_converter.convert_python_type(type(value)),
                self._storage_naming.generate_node_data_field_name(key),
                value,
            )
            for key, value in node_data.items()
        ]
