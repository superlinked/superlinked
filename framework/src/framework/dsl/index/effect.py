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

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.schema.event_schema_object import (
    MultipliedSchemaReference,
    SchemaReference,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["EffectModifier"] = False


@TypeValidator.wrap
@dataclass
class Effect:
    """
    An effect represents a conditional interaction within a `Space` where the
    `affecting_schema_reference` interacted with the `affected_schema_reference`.

    It allows you to real-time adjust embeddings based on interaction.
    e.g.: A `User` schema interacts with a `Post` schema, if `event.type == 'like'.
    """

    space: Space
    affected_schema_reference: SchemaReference
    affecting_schema_reference: SchemaReference | MultipliedSchemaReference
    filter_: ComparisonOperation[SchemaField]

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(space={self.space}, filter={self.filter_}, "
            f"affected_schema_reference={self.affected_schema_reference}, "
            f"affecting_schema_reference={self.affecting_schema_reference})"
        )


@TypeValidator.wrap
@dataclass
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
