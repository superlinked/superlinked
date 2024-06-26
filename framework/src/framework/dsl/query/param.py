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

from beartype.typing import Sequence, TypeAlias


class Param:
    """
    Class representing a parameter that will be provided during the execution of the query.

    Attributes:
        name (str): The name of the parameter.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the Param.

        Args:
            name (str): The name of the parameter.
        """
        self.name = name


ParamInputType: TypeAlias = (
    Sequence[str] | Sequence[float] | str | int | float | bool | None
)
ParamType: TypeAlias = ParamInputType | Param
NumericParamType: TypeAlias = float | int | Param
IntParamType: TypeAlias = int | Param
