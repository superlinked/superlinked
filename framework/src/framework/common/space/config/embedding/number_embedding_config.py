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

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidInputException,
    NotImplementedException,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)

LOG_BASE: int = 10


class Mode(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SIMILAR = "similar"


@dataclass(frozen=True)
class Scale:
    @abstractmethod
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        """
        This method should include all class members that define its functionality.
        """


@dataclass(frozen=True)
class LinearScale(Scale):
    @override
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__}


@dataclass(frozen=True)
class LogarithmicScale(Scale):
    @override
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        return {"class_name": type(self).__name__, "base": LOG_BASE}


@dataclass(frozen=True)
class NumberEmbeddingConfig(EmbeddingConfig[float]):
    min_value: float
    max_value: float
    mode: Mode
    scale: Scale
    negative_filter: float

    def __post_init__(self) -> None:
        self._validate_input()

    def _validate_input(self) -> None:
        if isinstance(self.scale, LogarithmicScale) and self.min_value < 0:
            raise InvalidInputException("Min value must be 0 or higher when using logarithmic scale.")
        if isinstance(self.scale, LogarithmicScale) and self.max_value < 0:
            raise InvalidInputException("Max value cannot be 0 when using logarithmic scale.")
        if self.min_value >= self.max_value:
            raise InvalidInputException(
                f"The maximum value ({self.max_value}) should be greater than the minimum value ({self.min_value})."
            )
        if self.negative_filter > 0:
            raise InvalidInputException(
                f"The negative filter value should not be more than 0. Value is: {self.negative_filter}"
            )

    @property
    @override
    def length(self) -> int:
        return 3

    @override
    def _get_embedding_config_parameters(self) -> dict[str, Any]:
        return {
            "class_name": type(self).__name__,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mode": self.mode.value,
            "scale": self.scale._get_embedding_config_parameters(),
            "negative_filter": self.negative_filter,
        }

    @property
    def negative_filter_indices(self) -> frozenset:
        return frozenset({2})

    @property
    @override
    def default_vector(self) -> Vector:
        if self.mode == Mode.SIMILAR:
            default_values = [0.0, 0.0, 0.0]
        elif self.mode == Mode.MINIMUM:
            default_values = [0.0, 1.0, 1.0]
        elif self.mode == Mode.MAXIMUM:
            default_values = [1.0, 0.0, 1.0]
        else:
            raise NotImplementedException("Unsupported mode.", mode=self.mode.name)
        return Vector(default_values, self.negative_filter_indices)

    def should_return_default(self, context: ExecutionContext) -> bool:
        return context.is_query_context and self.mode in {
            Mode.MINIMUM,
            Mode.MAXIMUM,
        }
