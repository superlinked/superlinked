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
from superlinked.framework.dsl.query.nlq.param_filler.query_param_model_validator_info import (
    QueryParamModelValidatorInfo,
)
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.space.space import Space

UNAFFECTING_VALUES = [constants.DEFAULT_NOT_AFFECTING_WEIGHT, None]


class QueryParamModelValidator:

    @classmethod
    def build(cls, clause_collector: NLQClauseCollector) -> PydanticDescriptorProxy[ModelValidatorDecoratorInfo]:
        validator_info = QueryParamModelValidatorInfo(clause_collector)
        return cls._create_model_validator(validator_info)

    @classmethod
    def _create_model_validator(
        cls, validator_info: QueryParamModelValidatorInfo
    ) -> PydanticDescriptorProxy[ModelValidatorDecoratorInfo]:
        @model_validator(mode="after")
        def validate(model: BaseModel | Any) -> Any:
            if isinstance(model, BaseModel):
                model_dict: dict[str, Any] = model.model_dump()
                cls._validate_with_vector_weights(
                    model_dict,
                    validator_info.with_vector_weight_param,
                    validator_info.space_weight_param_name_by_space,
                )
                cls._validate_allowed_values(model_dict, validator_info.allowed_values_by_param)
                cls._validate_similar_weights(model_dict, validator_info.similar_and_space_weight_param_names)
            return model

        return validate

    @classmethod
    def _validate_similar_weights(
        cls,
        model_dict: dict[str, Any],
        similar_and_space_weight_param_names: Sequence[tuple[str, str]],
    ) -> None:
        """Validate that space weights are filled when similar weights are present."""
        for similar_w_name, space_w_name in similar_and_space_weight_param_names:
            if (
                model_dict.get(similar_w_name) not in UNAFFECTING_VALUES
                and model_dict.get(space_w_name) in UNAFFECTING_VALUES
            ):
                raise ValueError(
                    f"If {similar_w_name} is not {constants.DEFAULT_NOT_AFFECTING_WEIGHT}/None,"
                    f" then set a positive value for the following field: {space_w_name}."
                )

    @classmethod
    def _validate_with_vector_weights(
        cls,
        model_dict: dict[str, Any],
        with_vector_weight_param: str | None,
        space_weight_param_name_by_space: Mapping[Space, str],
    ) -> None:
        """Validate that space weights are filled when with_vector weights are present."""
        if not with_vector_weight_param:
            return
        with_vector_weight = model_dict.get(with_vector_weight_param)
        if with_vector_weight in UNAFFECTING_VALUES:
            return

        unaffecting_space_weight_param_names = [
            param_name
            for param_name in space_weight_param_name_by_space.values()
            if model_dict.get(param_name) in UNAFFECTING_VALUES
        ]
        if unaffecting_space_weight_param_names:
            none_space_weight_params_text = ", ".join(sorted(unaffecting_space_weight_param_names))
            raise ValueError(
                f"If {with_vector_weight_param} is not {constants.DEFAULT_NOT_AFFECTING_WEIGHT}/None,"
                f" then set a positive value for the following fields: {none_space_weight_params_text}."
            )

    @classmethod
    def _validate_allowed_values(
        cls,
        model_dict: dict[str, Any],
        allowed_values_by_param: Mapping[str, set[ParamInputType]],
    ) -> None:
        """Validate that all params have value set that is allowed"""
        for param_name, allowed_values in allowed_values_by_param.items():
            returned_value = model_dict.get(param_name)
            if returned_value is None:
                continue
            if TypeValidator.is_sequence_safe(returned_value):
                if not all(value in allowed_values or value is None for value in returned_value):
                    raise ValueError(
                        f"The field {param_name} can only contain None or a subset of: "
                        f"{cls._format_allowed_values(allowed_values)}."
                    )
            elif returned_value not in allowed_values:
                raise ValueError(
                    f"The field {param_name} must be None or one of the following items: "
                    f"{cls._format_allowed_values(allowed_values)}."
                )

    @classmethod
    def _format_allowed_values(cls, allowed_values: set[ParamInputType]) -> str:
        allowed_values_text = ", ".join(sorted((str(v) for v in allowed_values)))
        return allowed_values_text
