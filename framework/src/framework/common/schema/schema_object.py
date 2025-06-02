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

from abc import abstractmethod
from dataclasses import dataclass

from beartype.typing import Any, Generic, Sequence, TypeVar, cast
from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    COMPARABLE_COMPARISON_OPERATION_TYPES,
    CONTAINS_COMPARISON_OPERATION_TYPES,
    EQUALITY_COMPARISON_OPERATION_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.exception import FieldException
from superlinked.framework.common.schema.schema_field_descriptor import (
    SchemaFieldDescriptor,
)
from superlinked.framework.common.util.collection_util import CollectionUtil

# Exclude from documentation.
# A better approach would be to separate this file into atomic objects,
# which is blocked due to circular dependency issues.
__pdoc__ = {}
__pdoc__["SchemaFieldDescriptor"] = False


# SchemaFieldType
SFT = TypeVar("SFT", bound=PythonTypes)
SchemaObjectT = TypeVar("SchemaObjectT", bound="SchemaObject")


class SchemaObject:
    """
    `@schema` decorated class that has multiple `SchemaField`s.

    Use it to represent your structured data to reference during the vector embedding process.
    """

    def __init__(self, base_cls: type) -> None:
        self._base_cls = base_cls
        self._schema_fields = self._init_schema_fields()
        self._schema_fields_by_name = {field.name: field for field in self._schema_fields}

    @abstractmethod
    def _init_schema_fields(self) -> Sequence[SchemaField]: ...

    @property
    def _base_class_name(self) -> str:
        return self._base_cls.__name__

    @property
    def _schema_name(self) -> str:
        return self._base_class_name

    @property
    def schema_fields(self) -> Sequence[SchemaField]:
        return self._schema_fields

    def __str__(self) -> str:
        schema_fields = ", ".join([f"(name={field.name}, type={field.type_.__name__})" for field in self.schema_fields])
        return f"{type(self).__name__}(schema_name={self._schema_name}, schema_fields=[{schema_fields}])"

    def _init_field(self: SchemaObjectT, field_descriptor: SchemaFieldDescriptor) -> SchemaField:
        value = field_descriptor.type_(field_descriptor.name, self, field_descriptor.nullable)
        setattr(self, field_descriptor.name, value)
        return value

    def _get_fields_by_names(self, field_names: Sequence[str]) -> list[SchemaField]:
        matched_fields = []
        missing_field_names = []

        for field_name in field_names:
            if field := self._schema_fields_by_name.get(field_name):
                matched_fields.append(field)
            else:
                missing_field_names.append(field_name)

        if missing_field_names:
            missing_field_names_text = ", ".join(missing_field_names)
            raise FieldException(f"Fields {missing_field_names_text} not found in schema {self._schema_name}.")

        return matched_fields


class SchemaField(ComparisonOperand, Generic[SFT]):
    """
    A SchemaField is a generic field of your `@schema` decorated class.

    `SchemaField`s are the basic building block for inputs that will be referenced in an embedding space.
    Sub-types of a `SchemaField` are typed data representations that you can use to transform and load data
    to feed the vector embedding process.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, type_: type[SFT], nullable: bool) -> None:
        super().__init__(SchemaField)
        self.name = name
        self.schema_obj = schema_obj
        self.type_ = type_
        self.nullable = nullable

    def parse(self, value: SFT) -> SFT:
        return value

    def __hash__(self) -> int:
        return hash((self.name, self.schema_obj))

    def __str__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"(name={self.name}, type={self.type_.__name__}, schema_object_name={self.schema_obj._schema_name})"
        )

    def as_type(self, value: Any) -> SFT:
        return cast(SFT, self.type_(value))

    @property
    @abstractmethod
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]: ...

    @staticmethod
    def _built_in_equal(left_operand: ComparisonOperand[SchemaField], right_operand: object) -> bool:
        if isinstance(left_operand, SchemaField) and isinstance(right_operand, SchemaField):
            return right_operand.name == left_operand.name and right_operand.schema_obj == left_operand.schema_obj
        return False

    @staticmethod
    def _built_in_not_equal(left_operand: ComparisonOperand[SchemaField], right_operand: object) -> bool:
        return not SchemaField._built_in_equal(left_operand, right_operand)


SchemaFieldT = TypeVar("SchemaFieldT", bound=SchemaField)


class String(SchemaField[str]):
    """
    Field of a schema that represents a string value.

    e.g.: `TextEmbeddingSpace` expects a String field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, str, nullable)

    def __add__(self, other: object) -> DescribedBlob:
        if not isinstance(other, Blob):
            raise TypeError(f"Operand must be of type {Blob.__name__}")
        return DescribedBlob(blob=other, description=self)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return EQUALITY_COMPARISON_OPERATION_TYPES


class Timestamp(SchemaField[int]):
    """
    Field of a schema that represents a unix timestamp.

    e.g.: `RecencySpace` expects a Timestamp field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, int, nullable)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return EQUALITY_COMPARISON_OPERATION_TYPES + COMPARABLE_COMPARISON_OPERATION_TYPES

    @override
    def as_type(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        return int(value.timestamp())


class Blob(SchemaField[BlobInformation]):
    """
    Field of a schema that represents a local/remote file path or an utf-8 encoded bytes string.

    e.g.: `ImageSpace` expects a blob field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, BlobInformation, nullable)

    def __add__(self, other: object) -> DescribedBlob:
        if not isinstance(other, String):
            raise TypeError(f"Operand must be of type {String.__name__}")
        return DescribedBlob(blob=self, description=other)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return []

    @override
    def as_type(self, value: Any) -> BlobInformation:
        # FAB-3256
        return cast(BlobInformation, value)


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

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, float, nullable)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return COMPARABLE_COMPARISON_OPERATION_TYPES


class Integer(Number[int]):
    """
    Field of a schema that represents an integer.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, int, nullable)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return EQUALITY_COMPARISON_OPERATION_TYPES + COMPARABLE_COMPARISON_OPERATION_TYPES


class Boolean(SchemaField[bool]):
    """
    Field of a schema that represents a boolean.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, bool, nullable)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return EQUALITY_COMPARISON_OPERATION_TYPES

    def is_(self, __value: bool) -> ComparisonOperation[SchemaField]:
        """
        Equivalent to equality comparison for boolean fields.
        This method exists to avoid linter errors when comparing boolean fields.
        """
        return self == __value

    def is_not_(self, __value: bool) -> ComparisonOperation[SchemaField]:
        """
        Equivalent to inequality comparison for boolean fields.
        This method exists to avoid linter errors when comparing boolean fields.
        """
        return self != __value


class FloatList(SchemaField[list[float]]):
    """
    Field of a schema that represents a vector.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, list[float], nullable)

    @override
    def parse(self, value: list[float]) -> list[float]:
        return value if isinstance(value, list) else [cast(float, value)]

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return []

    @override
    def as_type(self, value: Any) -> list[float]:
        return [float(val) for val in CollectionUtil.convert_single_item_to_list(value)]


class StringList(SchemaField[list[str]]):
    """
    Field of a schema that represents a list of strings.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, nullable: bool) -> None:
        super().__init__(name, schema_obj, list[str], nullable)

    @override
    def parse(self, value: list[str]) -> list[str]:
        return value if isinstance(value, list) else [cast(str, value)]

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return CONTAINS_COMPARISON_OPERATION_TYPES

    @override
    def as_type(self, value: Any) -> list[str]:
        return [str(val) for val in CollectionUtil.convert_single_item_to_list(value)]


@dataclass(frozen=True)
class DescribedBlob:
    blob: Blob
    description: String


ConcreteSchemaField = String | Timestamp | Float | Integer | Boolean | FloatList | StringList | Blob
ConcreteSchemaFieldT = TypeVar("ConcreteSchemaFieldT", bound="ConcreteSchemaField")
