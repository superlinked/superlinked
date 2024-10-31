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

from beartype.typing import Any, Generic, cast

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.space.space import SIT, Space


@dataclass
class SpaceFieldSet(Generic[SIT]):
    """
    A class representing a set of fields in a space.
    Attributes:
        space (Space): The space.
        fields (set[SchemaField]): The set of fields.
    """

    space: Space
    fields: set[SchemaField]

    def __post_init__(self) -> None:
        self.__schema_field_map = {field.schema_obj: field for field in self.fields}

    def _generate_space_input(self, value: PythonTypes) -> SIT:
        return cast(SIT, value)

    # TODO [FAI-2453]
    def get_field_for_schema(self, schema_: Any) -> SchemaField | None:
        return self.__schema_field_map.get(schema_)
