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

import asyncio
import threading

import nest_asyncio
from beartype.typing import Any, Coroutine, TypeVar

T = TypeVar("T")


class AsyncUtil:
    _loop_local = threading.local()

    @classmethod
    def run(cls, coroutine: Coroutine[Any, Any, T]) -> T:
        """Execute an async coroutine safely regardless of current event loop state."""
        loop = cls._get_loop()
        if loop and loop.is_running():
            return cls._handle_async_context(loop, coroutine)
        return cls._handle_sync_context(loop, coroutine)

    @classmethod
    def _apply_nest_asyncio(cls, loop: Any) -> None:
        """Apply nest_asyncio to handle nested execution"""
        if not hasattr(loop, "_nest_asyncio_patched"):
            nest_asyncio.apply(loop)

    @classmethod
    def _get_loop(cls) -> Any | None:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    @classmethod
    def _handle_async_context(cls, loop: Any, coroutine: Coroutine[Any, Any, T]) -> T:
        cls._apply_nest_asyncio(loop)
        future = asyncio.ensure_future(coroutine, loop=loop)
        return loop.run_until_complete(future)

    @classmethod
    def _handle_sync_context(cls, loop: Any, coroutine: Coroutine[Any, Any, T]) -> T:
        if not hasattr(cls._loop_local, "loop"):
            cls._loop_local.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop_local.loop)
        loop = cls._loop_local.loop
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        cls._apply_nest_asyncio(loop)
        future = asyncio.ensure_future(coroutine, loop=loop)
        return loop.run_until_complete(future)
