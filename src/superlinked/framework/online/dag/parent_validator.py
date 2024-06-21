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

from enum import Enum

from beartype.typing import Callable


class ParentValidationType(Enum):
    LESS_THAN_TWO_PARENTS = (lambda len: len < 2, "less than 2 parents")
    AT_LEAST_ONE_PARENT = (lambda len: len >= 1, "at least 1 parent")
    EXACTLY_ONE_PARENT = (lambda len: len == 1, "exactly 1 parent")
    NO_PARENTS = (lambda len: len == 0, "no parents")
    NO_VALIDATION = (lambda len: True, "no validation")

    validator: Callable[[int], bool]
    description: str

    def __new__(
        cls, validator: Callable[[int], bool], description: str
    ) -> ParentValidationType:
        obj = object.__new__(cls)
        obj.validator = validator
        obj.description = description
        return obj
