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

import asyncio
from dataclasses import dataclass, field
from itertools import accumulate

from beartype.typing import Awaitable, Callable, Generic, Sequence, TypeVar, cast

from superlinked.framework.common.exception import InvalidStateException

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True)
class DelayedRequest(Generic[InputT, OutputT]):
    inputs: Sequence[InputT]
    future: asyncio.Future[list[OutputT]] = field(
        default_factory=asyncio.Future, init=False, repr=False, compare=False, hash=False
    )


class DelayedEvaluator(Generic[InputT, OutputT]):
    """
    A batching evaluator that delays execution to accumulate multiple requests
    and process them together in a single operation.

    This class is useful for optimizing operations that benefit from batching,
    such as inference or database operations.

    Args:
        delay_ms: Delay in milliseconds before processing accumulated requests
        eval_fn: Async function that processes a batch of inputs and returns results
    """

    def __init__(self, delay_ms: int, eval_fn: Callable[[Sequence[InputT]], Awaitable[list[OutputT]]]) -> None:
        self._delay_ms = delay_ms
        self._evaluate_fn = eval_fn
        self._pending_requests: list[DelayedRequest[InputT, OutputT]] = []
        self._batch_task: asyncio.Task[None] | None = None
        self._lock = None if self._delay_ms <= 0 else asyncio.Lock()

    async def evaluate(self, inputs: Sequence[InputT]) -> list[OutputT]:
        if self._delay_ms <= 0:
            return await self._evaluate_fn(inputs)
        request = DelayedRequest[InputT, OutputT](inputs)
        if self._lock is None:
            raise InvalidStateException("Lock must not be None.")
        async with self._lock:
            self._pending_requests.append(request)
            if self._batch_task is None or self._batch_task.done():
                self._batch_task = asyncio.create_task(self._process_batch_after_delay())
        return await request.future

    async def _process_batch_after_delay(self) -> None:
        await asyncio.sleep(self._delay_ms / 1000)
        if self._lock is None:
            raise InvalidStateException("Lock must not be None.")
        async with self._lock:
            if not self._pending_requests:
                return
            requests = self._pending_requests.copy()
            self._pending_requests.clear()
        try:
            await self._process_batch_requests(requests)
        except Exception as e:
            for request in requests:
                if not request.future.done():
                    request.future.set_exception(e)
            raise
        await self._handle_when_other_request_arrived_during_sleep()

    async def _handle_when_other_request_arrived_during_sleep(self) -> None:
        """To avoid freezing requests"""
        if self._lock is None:
            raise InvalidStateException("Lock must not be None.")
        async with self._lock:
            if self._pending_requests:
                self._batch_task = asyncio.create_task(self._process_batch_after_delay())
            else:
                self._batch_task = None

    async def _process_batch_requests(self, requests: Sequence[DelayedRequest[InputT, OutputT]]) -> None:
        results = await self._evaluate_fn([input_item for request in requests for input_item in request.inputs])
        positions = [0] + list(accumulate(len(request.inputs) for request in requests))
        for request, start, end in zip(requests, positions, positions[1:]):
            if not request.future.done():
                result = cast(list[OutputT], None if results is None else results[start:end])
                request.future.set_result(result)
