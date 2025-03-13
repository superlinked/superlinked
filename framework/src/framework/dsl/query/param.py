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

from beartype.typing import Any, Sequence, TypeAlias
from PIL.Image import Image

from superlinked.framework.common.util.type_validator import TypeValidator

UNSET_PARAM_NAME = "__UNSET_PARAM_NAME__"


class Param:
    """
    Class representing a parameter that will be provided during the execution of the query.

    Attributes:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (ParamInputType | None, optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.
        options (list[ParamInputType] | set[ParamInputType] | None, optional): Allowed values for this parameter.
            If provided, only these values will be accepted. Defaults to None.
    """

    def __init__(
        self,
        name: str,
        description: str | None = None,
        default: ParamInputType | None = None,
        options: Sequence[ParamInputType | None] | None = None,
    ) -> None:
        """
        Initialize the Param.

        Args:
            name (str): The unique name of the parameter.
            description (str, optional): Description of the parameter. Used for natural language query.
                Defaults to None.
            default (ParamInputType, | None optional): Value to use if not overridden by query parameter.
                Natural language query will use defaults. Defaults to None.
            options (list[ParamInputType] | set[ParamInputType] | None, optional): Allowed values for this parameter.
                If provided, only these values will be accepted. Defaults to None.
        """
        self.name = name
        self.description = description
        self.default = default
        self.options = self.__init_options(self.name, options)
        if self.default is not None:
            self._validate_value_allowed(self.default)

    def __init_options(self, name: str, options: Sequence[ParamInputType | None] | None) -> set[ParamInputType | None]:
        if options and any(TypeValidator.is_sequence_safe(option) for option in options):
            raise ValueError(
                f"Sequence option item is not allowed for parameter {name}. " "Each option must be a single value."
            )
        return set(options) if options else set()

    def _validate_value_allowed(self, value: Any) -> None:
        if not self.options:
            return
        if TypeValidator.is_sequence_safe(value):
            if invalid_values := set(value).difference(self.options):
                raise ValueError(
                    f"Values {invalid_values} are not allowed for parameter {self.name}. "
                    f"Allowed values are: {self.options}"
                )
        elif value not in self.options:
            raise ValueError(
                f"Value {value} is not allowed for parameter {self.name}. " f"Allowed values are: {self.options}"
            )

    @staticmethod
    def init_default(default: ParamInputType | None = None) -> Param:
        return Param(UNSET_PARAM_NAME, default=default)


ParamInputType: TypeAlias = (
    Sequence[str] | Sequence[float] | Image | str | int | float | bool | tuple[str | None, str | None]
)
ParamType: TypeAlias = ParamInputType | None | Param
StringParamType: TypeAlias = str | Param
NumericParamType: TypeAlias = float | int | Param
IntParamType: TypeAlias = int | Param
