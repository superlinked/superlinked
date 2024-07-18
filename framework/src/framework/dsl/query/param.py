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

from beartype.typing import Generic, Sequence, TypeAlias, TypeVar

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["EvaluatedParam"] = False
__pdoc__["WeightedEvaluatedParam"] = False


class Param:
    """
    Class representing a parameter that will be provided during the execution of the query.

    Attributes:
        name (str): The name of the parameter.
    """

    def __init__(self, name: str, description: str | None = None) -> None:
        """
        Initialize the Param.

        Args:
            name (str): The name of the parameter.
            description (str, optional): Description of the parameter. Used for natural language query.
                Defaults to None.
        """
        self.name = name
        self.description = description


ParamInputType: TypeAlias = (
    Sequence[str] | Sequence[float] | str | int | float | bool | None
)
ParamType: TypeAlias = ParamInputType | Param
StringParamType: TypeAlias = str | Param
NumericParamType: TypeAlias = float | int | Param
IntParamType: TypeAlias = int | Param

PIT = TypeVar("PIT", bound=ParamInputType)


@dataclass
class EvaluatedParam(Generic[PIT]):
    param_name: str
    description: str | None
    value: PIT


@dataclass
class WeightedEvaluatedParam:
    value: EvaluatedParam[ParamInputType]
    weight: EvaluatedParam[float]
