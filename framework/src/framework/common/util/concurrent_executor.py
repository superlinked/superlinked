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
    def __init__(self, max_workers: int = MAX_WORKER_COUNT) -> None:
        self._max_workers = ConcurrentExecutor._determine_optimal_workers(max_workers)

    def execute_batched(
        self,
        func: Callable[..., Sequence[ReturnT]],
        items: Sequence[Any],
        batch_size: int | None = None,
        additional_args: Sequence[Any] | None = None,
        condition: bool = True,
    ) -> list[ReturnT]:
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
    ) -> list[ReturnT]:
        if condition and len(args_list) > 1:
            return self.execute_concurrently(func, args_list)
        return self.execute_sequentially(func, args_list)

    def execute_sequentially(self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]]) -> list[ReturnT]:
        return [func(*args) for args in args_list]

    def execute_concurrently(self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]]) -> list[ReturnT]:
        if len(args_list) <= 1:
            return self.execute_sequentially(func, args_list)
        worker_count = min(len(args_list), self._max_workers)
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(func, *args) for args in args_list]
            return [future.result() for future in futures]

    @staticmethod
    def _determine_optimal_workers(max_workers: int) -> int:
        cpu_count = os.cpu_count() or 1
        optimal_worker_count = cpu_count
        return min(max_workers, optimal_worker_count)
