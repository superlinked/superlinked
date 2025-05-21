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
from dataclasses import dataclass

from beartype.typing import Any
from typing_extensions import override


@dataclass(frozen=True)
class NormalizationConfig(ABC):
    @abstractmethod
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        """
        This method should include all class members that define its functionality, excluding the parent(s).
        """


class L1NormConfig(NormalizationConfig):
    @override
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__}


@dataclass(frozen=True)
class L2NormConfig(NormalizationConfig):
    @override
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__}


@dataclass(frozen=True)
class ConstantNormConfig(NormalizationConfig):
    length: float

    @override
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__, "length": self.length}


@dataclass(frozen=True)
class NoNormConfig(NormalizationConfig):
    @override
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__}


@dataclass(frozen=True)
class CategoricalNormConfig(NormalizationConfig):
    categories_count: int

    @override
    def _get_normalization_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__, "categories_count": self.categories_count}
