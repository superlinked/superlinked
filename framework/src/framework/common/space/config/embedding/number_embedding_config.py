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

from dataclasses import dataclass
from enum import Enum

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.embedding_type import (
    EmbeddingType,
)


class Mode(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SIMILAR = "similar"


@dataclass(frozen=True)
class Scale:
    pass


@dataclass(frozen=True)
class LinearScale(Scale):
    pass


@dataclass(frozen=True)
class LogarithmicScale(Scale):
    base: float = 10

    def __post_init__(self) -> None:
        if self.base <= 1:
            raise ValueError("Logarithmic function base must be larger than 1.")


class NumberEmbeddingConfig(EmbeddingConfig[float]):
    def __init__(
        self,
        min_value: float,
        max_value: float,
        mode: Mode,
        scale: Scale,
        negative_filter: float,
    ) -> None:
        super().__init__(EmbeddingType.NUMBER, float)
        self.min_value = min_value
        self.max_value = max_value
        self.mode = mode
        self.scale = scale
        self.negative_filter = negative_filter
        self._validate_input()
        self._default_vector = self.__init_default_vector()

    def _validate_input(self) -> None:
        if isinstance(self.scale, LogarithmicScale) and self.min_value < 0:
            raise ValueError(
                "Min value must be 0 or higher when using logarithmic scale."
            )
        if isinstance(self.scale, LogarithmicScale) and self.max_value < 0:
            raise ValueError("Max value cannot be 0 when using logarithmic scale.")
        if self.min_value >= self.max_value:
            raise ValueError(
                f"The maximum value ({self.max_value}) should be greater than the minimum value ({self.min_value})."
            )
        if self.negative_filter > 0:
            raise ValueError(
                f"The negative filter value should not be more than 0. Value is: {self.negative_filter}"
            )

    def __init_default_vector(self) -> Vector:
        if self.mode == Mode.SIMILAR:
            default_values = [0.0, 0.0, 0.0]
        elif self.mode == Mode.MINIMUM:
            default_values = [0.0, 1.0, 1.0]
        elif self.mode == Mode.MAXIMUM:
            default_values = [1.0, 0.0, 1.0]
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        return Vector(default_values)

    @property
    @override
    def length(self) -> int:
        return 3

    @property
    def default_vector(self) -> Vector:
        return self._default_vector

    @override
    def should_return_default(self, context: ExecutionContext) -> bool:
        return super().should_return_default(context) or (
            context.is_query_context
            and self.mode
            in {
                Mode.MINIMUM,
                Mode.MAXIMUM,
            }
        )

    @override
    def to_dict(self) -> dict[str, Any]:
        return super().to_dict() | {
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mode": self.mode,
            "scale": self.scale,
            "negative_filter": self.negative_filter,
        }
