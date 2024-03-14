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
from typing import Any, Generic, TypeVar

from superlinked.framework.common.interface.comparison_operand import ComparisonOperand

# Exclude from documentation.
# A better approach would be to separate this file into atomic objects,
# which is blocked due to circular dependency issues.
__pdoc__ = {}
__pdoc__["SchemaFieldDescriptor"] = False


# SchemaFieldType
SFT = TypeVar("SFT")
SchemaObjectT = TypeVar("SchemaObjectT", bound="SchemaObject")


class SchemaObject:
    """
    `@schema` decorated class that has multiple `SchemaField`s.

    Use it to represent your structured data to reference during the vector embedding process.
    """

    def __init__(self, base_cls: type, schema_name: str) -> None:
        self.__schema_name = schema_name
        self._base_cls = base_cls

    @property
    def _base_class_name(self) -> str:
        return self._base_cls.__name__

    @property
    def _schema_name(self) -> str:
        return self.__schema_name

    def _init_field(
        self: SchemaObjectT, field_descriptor: SchemaFieldDescriptor
    ) -> SchemaField:
        value = field_descriptor.type_(field_descriptor.name, self)
        setattr(self, field_descriptor.name, value)
        return value

    def _get_schema_fields(self) -> list[SchemaField]:
        return []


class SchemaField(ComparisonOperand, Generic[SFT]):
    """
    A SchemaField is a generic field of your `@schema` decorated class.

    `SchemaField`s are the basic building block for inputs that will be referenced in an embedding space.
    Sub-types of a `SchemaField` are typed data representations that you can use to transform and load data
    to feed the vector embedding process.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, type_: type[SFT]) -> None:
        super().__init__(SchemaField)
        self.name = name
        self.schema_obj = schema_obj
        self.type_ = type_

    def __hash__(self) -> int:
        return hash((self.name, self.schema_obj))

    @staticmethod
    def _original_equal(
        left_operand: ComparisonOperand[SchemaField], right_operand: object
    ) -> bool:
        if isinstance(left_operand, SchemaField) and isinstance(
            right_operand, SchemaField
        ):
            return (
                right_operand.name == left_operand.name
                and right_operand.schema_obj == left_operand.schema_obj
            )
        return False

    @staticmethod
    def _original_not_equal(
        left_operand: ComparisonOperand[SchemaField], right_operand: object
    ) -> bool:
        return not SchemaField._original_equal(left_operand, right_operand)


class String(SchemaField[str]):
    """
    Field of a schema that represents a string value.

    e.g.: `TextEmbeddingSpace` expects a String field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, str)


class Timestamp(SchemaField[int]):
    """
    Field of a schema that represents a unix timestamp.

    e.g.: `RecencySpace` expects a Timestamp field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, int)


NSFT = TypeVar("NSFT", float, int)


class Number(Generic[NSFT], SchemaField[NSFT]):
    """
    Field of a schema that represents a union of Float and Integer.

    e.g.: `NumberSpace` expects a Number field as an input.
    """


class Float(Number[float]):
    """
    Field of a schema that represents a float.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, float)


class Integer(Number[int]):
    """
    Field of a schema that represents an integer.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, int)


ConcreteSchemaField = String | Timestamp | Float | Integer
ConcreteSchemaFieldT = TypeVar("ConcreteSchemaFieldT", bound="ConcreteSchemaField")


@dataclass
class SchemaFieldDescriptor:
    name: str
    type_: type[ConcreteSchemaField]
    type_args: tuple[Any, ...]
