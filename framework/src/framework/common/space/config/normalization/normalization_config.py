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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.space.config.normalization.normalization_type import (
    NormalizationType,
)


@dataclass(frozen=True)
class NormalizationConfig:
    normalization_type: NormalizationType

    def to_dict(self) -> dict[str, Any]:
        return {"normalization_type": self.normalization_type.value}


class L2NormConfig(NormalizationConfig):
    def __init__(self) -> None:
        super().__init__(NormalizationType.L2_NORM)


class ConstantNormConfig(NormalizationConfig):
    def __init__(self, length: float) -> None:
        super().__init__(NormalizationType.CONSTANT_NORM)
        self.length = length

    @override
    def to_dict(self) -> dict[str, Any]:
        return super().to_dict() | {"length": self.length}

    @override
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self.length == other.length

    @override
    def __hash__(self) -> int:
        return hash((self.length, hash(super())))


class NoNormConfig(NormalizationConfig):
    def __init__(self) -> None:
        super().__init__(NormalizationType.NO_NORM)
