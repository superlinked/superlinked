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

from collections.abc import Mapping
from dataclasses import dataclass

from beartype.typing import Any


@dataclass
class ValuedDotSeparatedPath:
    path: str
    value: Any


class DotSeparatedPathUtil:
    @staticmethod
    def get(data: Mapping, path: str) -> Any:
        keys = path.split(".")

        current_data: Mapping = data
        # Iterate over all keys except the last one to navigate nested dictionaries
        for key in keys[:-1]:
            if current_data and isinstance(current_data, Mapping):
                current_data = current_data.get(key, {})

        # Get the value for the final key in the path
        return current_data.get(keys[-1])

    @staticmethod
    def set(data: dict, path: str, value: Any) -> None:
        keys = path.split(".")

        current_data = data
        # Iterate over all keys except the last one to navigate/create nested dictionaries
        for key in keys[:-1]:
            # Handle missing keys by creating new dictionaries
            current_data = current_data.setdefault(key, {})

        # Set the value for the final key in the path
        current_data[keys[-1]] = value

    @staticmethod
    def to_dict(path_value_pairs: list[ValuedDotSeparatedPath]) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for path_value_pair in path_value_pairs:
            DotSeparatedPathUtil.set(
                data,
                path_value_pair.path,
                path_value_pair.value,
            )
        return data
