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

from abc import ABC, abstractmethod

from beartype.typing import Any, Generic, TypeAlias, TypeVar
from typing_extensions import override

BaseT = TypeVar("BaseT")
TargetT = TypeVar("TargetT")


class TypeConverter(Generic[BaseT, TargetT], ABC):
    def __init__(self, base_type: TypeAlias, target_type: type[TargetT]) -> None:
        self.__base_type = base_type
        self.__target_type = target_type

    @property
    def base_type(self) -> TypeAlias:
        return self.__base_type

    @property
    def target_type(self) -> type[TargetT]:
        return self.__target_type

    def is_valid_base(self, value: Any) -> bool:
        return isinstance(value, self.base_type)

    @abstractmethod
    def convert(self, base: BaseT) -> TargetT: ...


class IntToFloatConverter(TypeConverter[int, float]):
    def __init__(self) -> None:
        super().__init__(int, float)

    @override
    def convert(self, base: int) -> float:
        return float(base)
