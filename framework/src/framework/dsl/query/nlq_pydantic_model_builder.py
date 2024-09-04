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
from pydantic import BaseModel, Field, create_model, model_validator

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operation_type import (
    LIST_TYPE_COMPATIBLE_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.query_param_information import ParamInfo
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["NLQPydanticModelBuilder"] = False

QUERY_MODEL_NAME = "QueryModel"


class NLQPydanticModelBuilder:

    def __init__(self, param_infos: Sequence[ParamInfo]) -> None:
        self.param_infos = param_infos

    def build(self) -> type[BaseModel]:
        field_info_by_name: dict[str, Any] = self._calculate_field_infos()
        field_info_by_name.update(self._get_model_validators_dict())
        model = create_model(QUERY_MODEL_NAME, **field_info_by_name)
        return model

    def _get_model_validators_dict(self) -> dict[str, dict[str, Any]]:
        similar_and_space_weight_param_names = (
            self._calculate_similar_and_space_weight_param_names()
        )

        @model_validator(mode="after")
        def check_space_weights_filled_when_similar_weight_filled(data: Any) -> Any:
            if isinstance(data, dict):
                for similar, space in similar_and_space_weight_param_names:
                    if not (
                        data.get(similar, 0.0) == 0.0 or data.get(space, 0.0) != 0.0
                    ):
                        raise ValueError(
                            f"If {similar} is not 0.0/None, then {space} must not be 0.0/None too."
                        )
            return data

        return {
            "__validators__": {
                "check_weights": check_space_weights_filled_when_similar_weight_filled
            }
        }

    def _calculate_similar_and_space_weight_param_names(self) -> list[tuple[str, str]]:
        space_weight_by_space: dict[Space, str] = {
            param_info.space: param_info.name
            for param_info in self.param_infos
            if param_info.is_weight
            and param_info.space is not None
            and param_info.schema_field is None
        }
        similar_and_space_weight_param_names: list[tuple[str, str]] = [
            (param_info.name, space_weight_by_space[param_info.space])
            for param_info in self.param_infos
            if param_info.is_weight
            and param_info.space is not None
            and param_info.schema_field is not None
            and param_info.space in space_weight_by_space
        ]
        return similar_and_space_weight_param_names

    def _calculate_field_infos(self) -> dict[str, tuple[type, Any]]:
        return {
            param_info.name: self._create_field(param_info)
            for param_info in self.param_infos
        }

    @classmethod
    def _create_field(cls, param_info: ParamInfo) -> tuple[type, Any]:
        field_type = cls._determine_type(
            param_info.op,
            param_info.is_weight,
            param_info.schema_field,
            param_info.value,
        )
        field_attrs: dict[str, Any] = {"description": param_info.description}
        is_filter_value = param_info.op is not None
        if is_filter_value or param_info.value is not None or param_info.is_weight:
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
        cls,
        op: ComparisonOperationType | None,
        is_weight: bool,
        schema_field: SchemaField | None,
        value: Any,
    ) -> type:
        if is_weight:
            return float
        if schema_field:
            type_should_be_list = op is not None and op in LIST_TYPE_COMPATIBLE_TYPES
            type_ = GenericClassUtil.get_single_generic_type(schema_field)
            return list[type_] if type_should_be_list else type_  # type: ignore[valid-type]
        if value is not None:
            return type(value)
        raise QueryException("NLQ field type cannot be determined.")
