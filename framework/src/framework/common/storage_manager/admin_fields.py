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

from beartype.typing import Sequence, cast

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.settings import settings
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FT, FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage_manager.header import Header
from superlinked.framework.common.storage_manager.storage_naming import StorageNaming


@dataclass(frozen=True)
class AdminFieldDescriptor:
    field: Field
    nullable: bool = False
    should_be_returned: bool = True  # Whether to include in query result

    def extract_value(self, field_data: dict[str, FieldData], _: type[FT]) -> FT | None:
        data = field_data.get(self.field.name)
        if not self.nullable and data is None:
            raise InvalidStateException("None value found for the non-null admin field.", field_name=self.field.name)
        value = data.value if data is not None else None
        return cast(FT, value)

    def create_field_data(
        self,
        value: PythonTypes | dict | None,
    ) -> FieldData | None:
        if value is None:
            if not self.nullable:
                raise InvalidStateException("None value cannot be assigned to admin field.", field_name=self.field.name)
            return None
        return FieldData.from_field(self.field, value)


class AdminFields:
    def __init__(self) -> None:
        name_to_field = {
            field_name: Field(FieldDataType.METADATA_STRING, field_name) for field_name in self.get_admin_field_names()
        }
        self.schema_id = AdminFieldDescriptor(name_to_field[StorageNaming.SCHEMA_INDEX_NAME])
        self.object_id = AdminFieldDescriptor(name_to_field[StorageNaming.OBJECT_ID_INDEX_NAME])
        self.origin_id = AdminFieldDescriptor(
            name_to_field[StorageNaming.ORIGIN_ID_INDEX_NAME],
            True,
            should_be_returned=settings.QUERY_TO_RETURN_ORIGIN_ID,
        )
        self.__admin_field_descriptors = [self.schema_id, self.object_id, self.origin_id]
        admin_fields = [admin_field_descriptor.field for admin_field_descriptor in self.__admin_field_descriptors]
        self.__admin_field_names = [admin_field.name for admin_field in admin_fields]
        self.__header_fields = [
            admin_field_descriptor.field
            for admin_field_descriptor in self.__admin_field_descriptors
            if admin_field_descriptor.should_be_returned
        ]

    @property
    def field_descriptors(self) -> Sequence[AdminFieldDescriptor]:
        return self.__admin_field_descriptors

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

    def __create_admin_field_data(
        self,
        value_by_admin_field: dict[AdminFieldDescriptor, PythonTypes | dict | None],
    ) -> Sequence[FieldData]:
        return [
            admin_field_data
            for admin_field_data in [
                admin_field.create_field_data(value) for admin_field, value in value_by_admin_field.items()
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
            raise InvalidStateException("None value found for the non-null admin field.")
        return value

    @classmethod
    def get_admin_field_names(cls) -> list[str]:
        return [StorageNaming.SCHEMA_INDEX_NAME, StorageNaming.OBJECT_ID_INDEX_NAME, StorageNaming.ORIGIN_ID_INDEX_NAME]
