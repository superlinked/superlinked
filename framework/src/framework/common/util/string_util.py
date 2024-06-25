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


from beartype.typing import Any


class StringUtil:
    @staticmethod
    def sort_and_serialize(dict_to_serialize: dict[str, Any]) -> str:
        def get_string_recursively(input_data: Any, outermost: bool = False) -> str:
            if isinstance(input_data, dict):
                string_values = [
                    f"{key}={get_string_recursively(value)}"
                    for key, value in sorted(input_data.items())
                ]
                return (
                    ", ".join(string_values)
                    if outermost
                    else "{" + ", ".join(string_values) + "}"
                )
            if isinstance(input_data, (set, list, tuple, frozenset)):
                values = ", ".join(
                    [
                        get_string_recursively(element)
                        for element in sorted(input_data, key=str)
                    ]
                )
                return f"[{values}]"
            return str(input_data)

        return get_string_recursively(dict_to_serialize, outermost=True)
