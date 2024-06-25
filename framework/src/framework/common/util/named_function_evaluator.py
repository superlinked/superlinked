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

from enum import Enum

from beartype.typing import Any

from superlinked.framework.common.dag.context import ExecutionContext


class NamedFunction(Enum):
    NOW = "now"


class NamedFunctionEvaluator:
    def evaluate(self, named_function: NamedFunction, context: ExecutionContext) -> Any:
        match named_function:
            case NamedFunction.NOW:
                return self.__now(context)

    def __now(self, context: ExecutionContext) -> int:
        return context.now()
