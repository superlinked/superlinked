# Copyright 2025 Superlinked, Inc
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

import asyncio

import nest_asyncio
from beartype.typing import Any, Coroutine, TypeVar

T = TypeVar("T")


class AsyncUtil:
    @staticmethod
    def run(coroutine: Coroutine[Any, Any, T]) -> T:
        """Execute an async coroutine safely regardless of current event loop state."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                nest_asyncio.apply(loop)
                return loop.run_until_complete(coroutine)
            return loop.run_until_complete(coroutine)
        except RuntimeError:
            return asyncio.run(coroutine)
