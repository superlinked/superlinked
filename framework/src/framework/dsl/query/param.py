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

from beartype.typing import Any, Sequence, TypeAlias, TypeVar
from PIL.ImageFile import ImageFile

from superlinked.framework.common.interface.evaluated import Evaluated

UNSET_PARAM_NAME = "__UNSET_PARAM_NAME_"


class Param:
    """
    Class representing a parameter that will be provided during the execution of the query.

    Attributes:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (Any, optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.
    """

    def __init__(
        self, name: str, description: str | None = None, default: Any | None = None
    ) -> None:
        """
        Initialize the Param.

        Args:
            name (str): The unique name of the parameter.
            description (str, optional): Description of the parameter. Used for natural language query.
                Defaults to None.
            default (Any, optional): Value to use if not overridden by query parameter.
                Natural language query will use defaults. Defaults to None.
        """
        self.name = name
        self.description = description
        self.default = default

    @staticmethod
    def init_evaluated(value: Any) -> Evaluated[Param]:
        if isinstance(value, Evaluated) and isinstance(value.item, Param):
            return Evaluated(value.item, value)
        return Evaluated(Param.init_default(), value)

    @staticmethod
    def init_default(default: Any | None = None) -> Param:
        return Param(UNSET_PARAM_NAME, None, default)


ParamInputType: TypeAlias = (
    Sequence[str]
    | Sequence[float]
    | ImageFile
    | str
    | int
    | float
    | bool
    | None
    | tuple[str | None, str | None]
)
ParamType: TypeAlias = ParamInputType | Param
StringParamType: TypeAlias = str | Param
NumericParamType: TypeAlias = float | int | Param
IntParamType: TypeAlias = int | Param

PIT = TypeVar("PIT", bound=ParamInputType)
