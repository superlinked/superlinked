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

import os
from concurrent.futures import ThreadPoolExecutor

from beartype.typing import Any, Callable, Sequence, TypeVar

from superlinked.framework.common.settings import Settings

ReturnT = TypeVar("ReturnT")

MAX_WORKER_COUNT = 32


class ConcurrentExecutor:
    _instance = None

    def __new__(cls) -> "ConcurrentExecutor":
        if cls._instance is None:
            cls._instance = super(ConcurrentExecutor, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_executor"):
            self._executor = ThreadPoolExecutor(max_workers=ConcurrentExecutor._determine_optimal_workers())

    def execute(self, func: Callable[..., ReturnT], args_list: Sequence[Sequence[Any]]) -> Sequence[ReturnT]:
        if not Settings().SUPERLINKED_EXPERIMENTAL_ENABLE_CONCURRENT_DAG_EVALUATION or len(args_list) <= 1:
            return [func(*args) for args in args_list]
        futures = [self._executor.submit(func, *args) for args in args_list]
        return [future.result() for future in futures]

    @staticmethod
    def _determine_optimal_workers() -> int:
        cpu_count = os.cpu_count() or 1
        optimal_worker_count = cpu_count * 2
        return min(MAX_WORKER_COUNT, optimal_worker_count)
