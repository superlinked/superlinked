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

import os
from concurrent.futures import ThreadPoolExecutor

from beartype.typing import Any, Callable, Sequence, TypeVar

ReturnT = TypeVar("ReturnT")

MAX_WORKER_COUNT = 32


class ConcurrentExecutor:
    _instance = None

    def __new__(cls) -> ConcurrentExecutor:
        if cls._instance is None:
            cls._instance = super(ConcurrentExecutor, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_executor"):
            self._max_workers = ConcurrentExecutor._determine_optimal_workers()
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

    def execute_batched(
        self,
        func: Callable[..., Sequence[ReturnT]],
        items: Sequence[Any],
        batch_size: int | None = None,
        additional_args: Sequence[Any] | None = None,
        condition: bool = True,
    ) -> Sequence[ReturnT]:
        """Process items in batches with concurrent execution within each batch."""
        if batch_size is None:
            batch_size = max(1, len(items) // self._max_workers)
        if additional_args is None:
            additional_args = []
        args_lists = [[items[i : i + batch_size]] + list(additional_args) for i in range(0, len(items), batch_size)]
        batch_results = self.execute(func, args_lists, condition)
        return [item for batch in batch_results for item in batch]

    def execute(
        self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]], condition: bool = True
    ) -> Sequence[ReturnT]:
        if condition and len(args_list) > 1:
            return self.execute_concurrently(func, args_list)
        return self.execute_sequentially(func, args_list)

    def execute_sequentially(
        self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]]
    ) -> Sequence[ReturnT]:
        return [func(*args) for args in args_list]

    def execute_concurrently(
        self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]]
    ) -> Sequence[ReturnT]:
        if len(args_list) <= 1:
            return self.execute_sequentially(func, args_list)
        futures = [self._executor.submit(func, *args) for args in args_list]
        return [future.result() for future in futures]

    @staticmethod
    def _determine_optimal_workers() -> int:
        cpu_count = os.cpu_count() or 1
        optimal_worker_count = cpu_count
        return min(MAX_WORKER_COUNT, optimal_worker_count)
