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


from __future__ import annotations

from dataclasses import dataclass

from beartype.typing import Any, Sequence, cast

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.storage.entity_id import EntityId
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FT, FieldData
from superlinked.framework.common.storage.field_data_type import FieldDataType
from superlinked.framework.common.storage_manager.header import Header
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming


@dataclass(frozen=True)
class AdminFieldDescriptor:
    field: Field
    nullable: bool = False
    is_header: bool = True

    def extract_value(self, field_data: dict[str, FieldData], _: type[FT]) -> FT | None:
        data = field_data.get(self.field.name)
        if not self.nullable and data is None:
            raise ValueError(
                f"None value found for the non-null {self.field.name} admin field."
            )
        value = data.value if data is not None else None
        return cast(FT, value)

    def create_field_data(
        self,
        value: PythonTypes | dict | None,
    ) -> FieldData | None:
        if value is None:
            if not self.nullable:
                raise ValueError(
                    f"None value cannot be assigned to {self.field.name} admin field."
                )
            return None
        return FieldData.from_field(self.field, value)


class AdminFields:
    def __init__(self) -> None:
        self.schema_id = AdminFieldDescriptor(
            Field(FieldDataType.STRING, StorageNaming.SCHEMA_INDEX_NAME)
        )
        self.object_id = AdminFieldDescriptor(
            Field(FieldDataType.STRING, StorageNaming.OBJECT_ID_INDEX_NAME)
        )
        self.origin_id = AdminFieldDescriptor(
            Field(FieldDataType.STRING, StorageNaming.ORIGIN_ID_INDEX_NAME), True
        )
        self.object_json = AdminFieldDescriptor(
            Field(FieldDataType.JSON, StorageNaming.OBJECT_JSON_INDEX_NAME), True, False
        )
        admin_field_descriptors = [
            self.schema_id,
            self.object_id,
            self.origin_id,
            self.object_json,
        ]
        admin_fields = [
            admin_field_descriptor.field
            for admin_field_descriptor in admin_field_descriptors
        ]
        self.__admin_field_names = [admin_field.name for admin_field in admin_fields]
        self.__header_fields = [
            admin_field_descriptor.field
            for admin_field_descriptor in admin_field_descriptors
            if admin_field_descriptor.is_header
        ]

    @property
    def header_fields(self) -> Sequence[Field]:
        return self.__header_fields

    def is_admin_field(self, field: Field) -> bool:
        return field.name in self.__admin_field_names

    def create_header_field_data(
        self,
        entity_id: EntityId,
        origin_id: str | None = None,
    ) -> Sequence[FieldData]:
        return self.__create_admin_field_data(
            {
                self.schema_id: entity_id.schema_id,
                self.object_id: entity_id.object_id,
                self.origin_id: origin_id,
            }
        )

    def create_object_json_field_data(
        self, object_json: dict[str, Any]
    ) -> FieldData | None:
        field_data = self.__create_admin_field_data({self.object_json: object_json})
        return field_data[0] if field_data else None

    def __create_admin_field_data(
        self,
        value_by_admin_field: dict[AdminFieldDescriptor, PythonTypes | dict | None],
    ) -> Sequence[FieldData]:
        return [
            admin_field_data
            for admin_field_data in [
                admin_field.create_field_data(value)
                for admin_field, value in value_by_admin_field.items()
            ]
            if admin_field_data is not None
        ]

    def extract_header(self, field_data: dict[str, FieldData]) -> Header:
        return Header(
            self._check_none_field(self.schema_id.extract_value(field_data, str)),
            self._check_none_field(self.object_id.extract_value(field_data, str)),
            self.origin_id.extract_value(field_data, str),
        )

    def _check_none_field(self, value: FT | None) -> FT:
        if value is None:
            raise ValueError("None value found for the non-null admin field.")
        return value

    def extract_object_json_field_data(
        self, field_data: dict[str, FieldData]
    ) -> dict[str, Any] | None:
        return self.object_json.extract_value(field_data, dict[str, Any])
