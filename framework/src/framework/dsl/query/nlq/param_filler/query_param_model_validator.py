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

from beartype.typing import Any, Mapping, Sequence
from pydantic import BaseModel, model_validator
from pydantic._internal._decorators import (
    ModelValidatorDecoratorInfo,
    PydanticDescriptorProxy,
)

from superlinked.framework.common.const import constants
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.query.nlq.nlq_clause_collector import NLQClauseCollector
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.query.space_weight_param_info import SpaceWeightParamInfo

UNAFFECTING_VALUES = [constants.DEFAULT_NOT_AFFECTING_WEIGHT, None]


class QueryParamModelValidator:
    @classmethod
    def build(cls, clause_collector: NLQClauseCollector) -> PydanticDescriptorProxy[ModelValidatorDecoratorInfo]:
        allowed_values_by_param = {
            QueryClause.get_param(param).name: allowed_values
            for clause_handler in clause_collector.clause_handlers
            for param in clause_handler.clause.params
            if (allowed_values := clause_handler.get_allowed_values(param))
        }
        return cls._create_model_validator(clause_collector.space_weight_param_info, allowed_values_by_param)

    @classmethod
    def _create_model_validator(
        cls,
        space_weight_param_info: SpaceWeightParamInfo,
        allowed_values_by_param: dict[str, set[ParamInputType | None]],
    ) -> PydanticDescriptorProxy[ModelValidatorDecoratorInfo]:
        @model_validator(mode="after")
        def validate(model: BaseModel | Any) -> Any:
            if isinstance(model, BaseModel):
                model_dict: dict[str, Any] = model.model_dump()
                instructions: list[str] = []
                instructions.extend(cls._calculate_space_weights_instructions(model_dict, space_weight_param_info))
                instructions.extend(cls._calculate_allowed_values_instructions(model_dict, allowed_values_by_param))
                if instructions:
                    raise ValueError("The following issues were found: \n " + " \n ".join(instructions))
            return model

        return validate

    @classmethod
    def _calculate_space_weights_instructions(
        cls,
        model_dict: Mapping[str, Any],
        space_weight_param_info: SpaceWeightParamInfo,
    ) -> Sequence[str]:
        def is_affecting_weight_with_unaffecting_space_weight(
            space_weight_name: str, weight_names: Sequence[str]
        ) -> bool:
            return model_dict.get(space_weight_name) in UNAFFECTING_VALUES and any(
                model_dict.get(weight_name) not in UNAFFECTING_VALUES for weight_name in weight_names
            )

        instructions = []
        for space, weight_names in space_weight_param_info.param_names_by_space.items():
            if (
                space_weight_name := space_weight_param_info.global_param_name_by_space.get(space)
            ) is not None and is_affecting_weight_with_unaffecting_space_weight(space_weight_name, weight_names):
                instructions.append(
                    f"As {weight_names} are set, {space_weight_name} must be also set to a positive value."
                )
        return instructions

    @classmethod
    def _calculate_allowed_values_instructions(
        cls,
        model_dict: Mapping[str, Any],
        allowed_values_by_param: Mapping[str, set[ParamInputType | None]],
    ) -> Sequence[str]:
        """Validate that all params have value set that is allowed"""
        instructions = []
        for param_name, allowed_values in allowed_values_by_param.items():
            returned_value = model_dict.get(param_name)
            if returned_value is None:
                continue
            if TypeValidator.is_sequence_safe(returned_value):
                if any(value is not None and value not in allowed_values for value in returned_value):
                    instructions.append(
                        f"The field {param_name} can only contain None or a subset of: "
                        f"{cls._format_allowed_values(allowed_values)}."
                    )
            elif returned_value not in allowed_values:
                instructions.append(
                    f"The field {param_name} must be None or one of the following items: "
                    f"{cls._format_allowed_values(allowed_values)}."
                )
        return instructions

    @classmethod
    def _format_allowed_values(cls, allowed_values: set[ParamInputType | None]) -> str:
        allowed_values_text = ", ".join(sorted((str(v) for v in allowed_values)))
        return allowed_values_text
