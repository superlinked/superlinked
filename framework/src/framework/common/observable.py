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
from abc import ABC, abstractmethod

from beartype.typing import Generic, Sequence, TypeVar, cast
from typing_extensions import override

from superlinked.framework.common.util.collection_util import CollectionUtil

PublishedMessageT = TypeVar("PublishedMessageT")


class Subscriber(ABC, Generic[PublishedMessageT]):
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def update(self, messages: Sequence[PublishedMessageT]) -> None:
        pass


ReceivedMessageT = TypeVar("ReceivedMessageT")


class TransformerPublisher(Generic[ReceivedMessageT, PublishedMessageT]):
    def __init__(self, chunk_size: int = 1) -> None:
        self._chunk_size = chunk_size
        self._pre_transform_subscribers: list[Subscriber[ReceivedMessageT]] = []
        self._subscribers: list[Subscriber[PublishedMessageT]] = []

    def register_pre_transform(self, subscriber: Subscriber[ReceivedMessageT]) -> None:
        self._pre_transform_subscribers.append(subscriber)

    def unregister_pre_transform(self, subscriber: Subscriber[ReceivedMessageT]) -> None:
        self._pre_transform_subscribers.remove(subscriber)

    def register(self, subscriber: Subscriber[PublishedMessageT]) -> None:
        self._subscribers.append(subscriber)

    def unregister(self, subscriber: Subscriber[PublishedMessageT]) -> None:
        self._subscribers.remove(subscriber)

    @abstractmethod
    async def transform(self, message: ReceivedMessageT) -> list[PublishedMessageT]:
        pass

    async def _dispatch(self, messages: ReceivedMessageT | Sequence[ReceivedMessageT]) -> None:
        messages = cast(
            Sequence[ReceivedMessageT],
            ([messages] if not isinstance(messages, Sequence) or isinstance(messages, str) else messages),
        )
        pre_transform_subscriber_tasks = [
            pre_transform_subscriber.update(batch)
            for batch in CollectionUtil.chunk_list(data=messages, chunk_size=self._chunk_size)
            for pre_transform_subscriber in self._pre_transform_subscribers
        ]
        await asyncio.gather(*pre_transform_subscriber_tasks)
        transform_tasks = [self.transform(message) for message in messages]
        transform_results = await asyncio.gather(*transform_tasks)
        transformed_messages = [transformed_message for result in transform_results for transformed_message in result]
        subscriber_tasks = [
            subscriber.update(transformed_batch)
            for transformed_batch in CollectionUtil.chunk_list(data=transformed_messages, chunk_size=self._chunk_size)
            for subscriber in self._subscribers
        ]
        await asyncio.gather(*subscriber_tasks)


class Publisher(
    TransformerPublisher[PublishedMessageT, PublishedMessageT],
    Generic[PublishedMessageT],
):
    @override
    async def transform(self, message: PublishedMessageT) -> list[PublishedMessageT]:
        return [message]
