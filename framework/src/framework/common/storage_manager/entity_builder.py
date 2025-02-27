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


from beartype.typing import Any, Mapping, Sequence

from superlinked.framework.common.data_types import NodeDataTypes, PythonTypes
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaField,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.storage.entity.entity import Entity
from superlinked.framework.common.storage.entity.entity_data import EntityData
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field_type_converter import FieldTypeConverter
from superlinked.framework.common.storage_manager.admin_fields import AdminFields
from superlinked.framework.common.storage_manager.node_result_data import NodeResultData
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming


class EntityBuilder:
    def __init__(
        self,
        storage_naming: StorageNaming,
    ) -> None:
        self._storage_naming = storage_naming
        self._admin_fields = AdminFields()

    def compose_entity_id(self, schema_id: str, object_id: str) -> EntityId:
        return EntityId(schema_id, object_id)

    def compose_entity(self, entity_id: EntityId, fields: Sequence[Field]) -> Entity:
        return Entity(entity_id, {field.name: field for field in fields})

    def convert_schema_field_to_field(self, schema_field: SchemaField) -> Field:
        return Field(
            FieldTypeConverter.convert_schema_field_type(type(schema_field)),
            self._storage_naming.generate_field_name_from_schema_field(schema_field),
        )

    def convert_parsed_schema_field_to_field_data(self, parsed_schema_field: ParsedSchemaField) -> FieldData:
        field = self.convert_schema_field_to_field(parsed_schema_field.schema_field)
        return FieldData.from_field(field, parsed_schema_field.value)

    def compose_entity_data(
        self,
        schema_id: str,
        object_id: str,
        field_data: Sequence[FieldData],
        origin_id: str | None = None,
    ) -> EntityData:
        entity_id = self.compose_entity_id(schema_id, object_id)
        admin_field_data = list(self._admin_fields.create_header_field_data(entity_id, origin_id))
        return EntityData(entity_id, {fd.name: fd for fd in (list(field_data) + admin_field_data)})

    def compose_entity_data_from_parsed_schema(self, parsed_schema: ParsedSchema) -> EntityData:
        return self.compose_entity_data(
            parsed_schema.schema._base_class_name,
            parsed_schema.id_,
            [
                self.convert_parsed_schema_field_to_field_data(parsed_schema_field)
                for parsed_schema_field in parsed_schema.fields
            ],
        )

    def compose_entity_data_from_node_result(self, node_data: NodeResultData) -> EntityData:
        field_data = [self.compose_field_data(node_data.node_id, node_data.result)] if node_data.result else []
        return self.compose_entity_data(node_data.schema_id, node_data.object_id, field_data, node_data.origin_id)

    def parse_schema_field_data(
        self,
        schema_field_data: FieldData,
        schema_field_by_field_name: Mapping[str, SchemaField],
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
                for field_data in entity_data.field_data.values()
            ],
        )

    def compose_field_from_node_data_descriptor(
        self, node_id: str, node_data_key: str, node_data_type: type[PythonTypes]
    ) -> Field:
        return self.compose_field(
            self._storage_naming.generate_node_data_field_name(node_id, node_data_key),
            node_data_type,
        )

    def compose_field(
        self,
        field_name: str,
        field_value_type: type,
    ) -> Field:
        return Field(
            FieldTypeConverter.convert_node_data_type(field_value_type),
            field_name,
        )

    def compose_field_data(self, field_name: str, field_value: NodeDataTypes) -> FieldData:
        return FieldData(
            FieldTypeConverter.convert_node_data_type(type(field_value)),
            field_name,
            field_value,
        )

    def compose_field_data_from_node_data(self, node_id: str, node_data: dict[str, Any]) -> Sequence[FieldData]:
        return [
            FieldData(
                FieldTypeConverter.convert_node_data_type(type(value)),
                self._storage_naming.generate_node_data_field_name(node_id, key),
                value,
            )
            for key, value in node_data.items()
            if value is not None
        ]
