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

import datetime
from dataclasses import dataclass

from superlinked.framework.common.util.type_validator import TypeValidator


@TypeValidator.wrap
@dataclass(frozen=True)
class EffectModifier:
    max_age_delta: datetime.timedelta | None = None
    max_count: int | None = None
    temperature: int | float = 0.5

    def __post_init__(self) -> None:
        if not 0 <= self.temperature <= 1:
            raise ValueError("temperature must be between 0 and 1.")
        if self.max_age_delta is not None and self.max_age_delta.total_seconds() == 0:
            raise ValueError("max_age cannot be 0 seconds.")
        if self.max_count is not None and self.max_count < 0:
            raise ValueError("max_count cannot be smaller than 0.")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(max_age={self.max_age_delta},"
            f"max_count={self.max_count}, "
            f"temperature={self.temperature})"
        )
