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

from beartype.typing import Any, Sequence
from pydantic import BaseModel, Field, create_model

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.query_param_information import ParamInfo

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["NLQPydanticModelBuilder"] = False

QUERY_MODEL_NAME = "QueryModel"


class NLQPydanticModelBuilder:

    def __init__(self, param_infos: Sequence[ParamInfo]) -> None:
        self.param_infos = param_infos

    def build(self) -> type[BaseModel]:
        field_info_by_name: dict[str, Any] = self._calculate_field_infos()
        model = create_model(QUERY_MODEL_NAME, **field_info_by_name)
        return model

    def _calculate_field_infos(self) -> dict[str, tuple[type, Any]]:
        return {
            param_info.name: self._create_field(param_info)
            for param_info in self.param_infos
        }

    @classmethod
    def _create_field(cls, param_info: ParamInfo) -> tuple[type, Any]:
        field_type = cls._determine_type(
            param_info.is_weight,
            param_info.schema_field,
            param_info.value,
        )
        field_attrs: dict[str, Any] = {
            "description": param_info.description,
            "json_schema_extra": cls._create_json_schema_extra(param_info),
        }
        if param_info.value is not None or param_info.is_weight:
            field_attrs["default"] = param_info.value
        field = Field(**field_attrs)  # type: ignore [pydantic-field]
        return field_type, field

    @classmethod
    def _create_json_schema_extra(cls, param_info: ParamInfo) -> dict[str, Any]:
        extras = {
            "space": type(param_info.space).__name__ if param_info.space else None,
            "schema_field": (
                param_info.schema_field.name if param_info.schema_field else None
            ),
        }
        return {k: v for k, v in extras.items() if v is not None}

    @classmethod
    def _determine_type(
        cls, is_weight: bool, schema_field: SchemaField | None, value: Any
    ) -> type:
        if is_weight:
            return float
        if schema_field:
            return GenericClassUtil.get_single_generic_type(schema_field)
        if value is not None:
            return type(value)
        raise QueryException("NLQ field type cannot be determined.")
