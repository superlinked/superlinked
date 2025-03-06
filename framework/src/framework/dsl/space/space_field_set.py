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

from beartype.typing import Any, Generic, Sequence, cast

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.common.util.lazy_property import lazy_property
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
    allowed_param_types: Sequence[type] | None = None

    def __post_init__(self) -> None:
        self._schema_field_map = {field.schema_obj: field for field in self.fields}
        self._input_type: type[SIT] = GenericClassUtil.get_generic_types(self.space)[1]
        self._fields_id = self.__generate_fields_id(self.fields)

    @lazy_property
    def validated_allowed_param_types(self) -> Sequence[type]:
        if self.allowed_param_types is None:
            return [self.input_type]
        return self.allowed_param_types

    @property
    def input_type(self) -> type[SIT]:
        return self._input_type

    @property
    def fields_id(self) -> str:
        return self._fields_id

    @property
    def field_names_text(self) -> Sequence[str]:
        return ",".join([f"{field.schema_obj._schema_name}.{field.name}" for field in self.fields])

    def _generate_space_input(self, value: PythonTypes) -> SIT:
        return cast(SIT, value)

    def get_field_for_schema(self, schema_: Any) -> SchemaField | None:
        return self._schema_field_map.get(schema_)

    def __generate_fields_id(self, fields: set[SchemaField]) -> str:
        field_ids = [f"{field.schema_obj._schema_name}_{field.name}" for field in fields]
        field_ids.sort()
        return "_".join(field_ids)
