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

from dataclasses import dataclass, field

from beartype.typing import Any, Mapping, Sequence, get_args

from superlinked.framework.common.interface.type_converter import TypeConverter
from superlinked.framework.common.util.generic_class_util import GenericClassUtil


@dataclass(frozen=True)
class ValidatedValue:
    is_valid: bool
    value: Any


@dataclass(frozen=True)
class TypeDescriptor:
    original_type: type
    is_list: bool
    valid_types: tuple[type, ...] = field(default_factory=tuple[type, ...])
    converter: TypeConverter | None = None

    def validate_value(self, value: Any) -> ValidatedValue:
        if value is None:
            return ValidatedValue(True, [] if self.is_list else None)
        if not self.is_list and isinstance(value, self.valid_types):
            return ValidatedValue(True, self.__convert(value))
        value = value if isinstance(value, list) else [value]
        if self.is_list and all(isinstance(item, self.valid_types) for item in value):
            return ValidatedValue(True, [self.__convert(item) for item in value])
        return ValidatedValue(False, value)

    @staticmethod
    def from_types(
        types: Sequence[type],
        valid_type_by_type: Mapping[type, tuple[type, ...]],
        converter_by_type: Mapping[type, TypeConverter],
    ) -> list[TypeDescriptor]:
        def get_valid_types(item_type: type) -> tuple[type, ...]:
            return valid_type_by_type.get(item_type, (item_type,))

        def create_type_descriptor(type_: type) -> TypeDescriptor:
            # Currently we only support list type "generics". For union types you can pass multiple types.
            if GenericClassUtil.if_not_class_get_origin(type_) is list:
                type_arg = get_args(type_)[0]
                return TypeDescriptor(
                    original_type=type_,
                    is_list=True,
                    valid_types=get_valid_types(type_arg),
                    converter=converter_by_type.get(type_arg),
                )
            return TypeDescriptor(
                original_type=type_,
                is_list=False,
                valid_types=get_valid_types(type_),
                converter=converter_by_type.get(type_),
            )

        return [create_type_descriptor(type_) for type_ in types]

    def __convert(self, value: Any) -> Any:
        if self.converter and self.converter.is_valid_base(value):
            return self.converter.convert(value)
        return value

    def __str__(self) -> str:
        plurality = "list of" if self.is_list else "single"
        valid_types_str = "|".join([type_.__name__ for type_ in self.valid_types])
        plurality_syllable = "(s)" if self.is_list else ""
        return f"A {plurality} {valid_types_str}{plurality_syllable}"
