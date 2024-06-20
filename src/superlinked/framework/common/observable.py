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

from abc import ABC, abstractmethod

from beartype.typing import Generic, TypeVar

# PublisherMessage
PM = TypeVar("PM")


class Subscriber(ABC, Generic[PM]):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def update(self, messages: list[PM]) -> None:
        pass


class Publisher(Generic[PM]):
    def __init__(self) -> None:
        self.subscribers: list[Subscriber] = []

    def register(self, subscriber: Subscriber[PM]) -> None:
        self.subscribers.append(subscriber)

    def unregister(self, subscriber: Subscriber[PM]) -> None:
        self.subscribers.remove(subscriber)

    def _dispatch(self, messages: list[PM]) -> None:
        for subscriber in self.subscribers:
            subscriber.update(messages)
