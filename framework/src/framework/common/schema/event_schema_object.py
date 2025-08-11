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

from abc import ABC
from types import UnionType

from beartype.typing import Any, Generic, Sequence, TypeVar, cast
from typing_extensions import override

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.interface.has_multiplier import HasMultiplier
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    SchemaField,
)

# Referenced schema type
RST = TypeVar("RST")
CREATED_AT_FIELD_NAME = "created_at"


class SchemaReference(SchemaField[str], HasMultiplier, Generic[RST]):
    """
    Schema reference used within an `EventSchema` to reference other schemas.
    """

    def __init__(
        self,
        name: str,
        schema_obj: EventSchemaObject,
        referenced_schema: type[RST],
    ) -> None:
        SchemaField.__init__(self, name, schema_obj, str, nullable=False)
        HasMultiplier.__init__(self)
        if not issubclass(referenced_schema, IdSchemaObject):
            raise InvalidInputException(f"referenced_schema ({referenced_schema}) is not a subclass of IdSchemaObject")
        self.__referenced_schema = referenced_schema

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return []

    def __str__(self) -> str:

        return (
            f"{type(self).__name__}(name={self.name}, schema_obj={self.schema_obj._schema_name}, "
            f"referenced_schema={self.__referenced_schema.__name__})"
        )

    @property
    def _referenced_schema(self) -> type[RST]:
        return self.__referenced_schema

    def __mul__(self, other: float | int) -> MultipliedSchemaReference:
        return MultipliedSchemaReference(self) * other

    def __rmul__(self, other: float | int) -> MultipliedSchemaReference:
        return MultipliedSchemaReference(self) * other


class MultipliedSchemaReference(HasMultiplier, Generic[RST]):
    def __init__(self, schema_reference: SchemaReference[RST], multiplier: float = 1.0) -> None:
        super().__init__(multiplier)
        self.__validate_multiplier()
        self.schema_reference = schema_reference

    def __validate_multiplier(self) -> None:
        if self.multiplier == 0:
            raise InvalidInputException(f"{self.__class__.__name__} cannot have 0 (zero) as its multiplier.")

    def __mul__(self, other: float | int) -> MultipliedSchemaReference:
        multiplier = self.multiplier * other
        return MultipliedSchemaReference(self.schema_reference, multiplier)

    def __rmul__(self, other: float | int) -> MultipliedSchemaReference:
        return self * other


class CreatedAtField(SchemaField[int]):
    """
    A class representing creation time. A unix timestamp field in a schema object.
    """

    def __init__(self, schema_obj: EventSchemaObject, created_at_field_name: str) -> None:
        super().__init__(created_at_field_name, schema_obj, int, nullable=False)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return []

    @override
    def as_type(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        return int(value.timestamp())


class EventSchemaObject(IdSchemaObject, ABC):
    """
    Custom decorated event schema class.
    Event schemas can be used to reference other schema and to define interactions between schemas.
    """

    def __init__(
        self,
        base_cls: type,
        id_field_name: str,
        created_at_field_name: str,
    ) -> None:
        super().__init__(base_cls, id_field_name)
        self.__created_at = CreatedAtField(self, created_at_field_name)
        if created_at_field_name != CREATED_AT_FIELD_NAME:
            setattr(self, created_at_field_name, self.__created_at)

    @property
    def created_at(self) -> CreatedAtField:
        return self.__created_at

    @override
    def _init_field(self, field_descriptor: SchemaFieldDescriptor) -> SchemaField:
        if field_descriptor.type_ == SchemaReference:
            if len(field_descriptor.arg_types) != 1:
                raise InvalidInputException(
                    (
                        f"Badly annotated SchemaReference ({field_descriptor.arg_types}). ",
                        "SchemaReference should be annotated with the referred schema object type.",
                    )
                )
            value: SchemaReference = SchemaReference(field_descriptor.name, self, field_descriptor.arg_types[0])
            setattr(self, field_descriptor.name, value)
            return value
        return super()._init_field(field_descriptor)

    @override
    @staticmethod
    def get_schema_field_type() -> UnionType:
        return cast(UnionType, ConcreteSchemaField | SchemaReference)
