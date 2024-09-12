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

from abc import abstractmethod

from beartype.typing import Generic

from superlinked.framework.queue.interface.message_converter import (
    MessageConverter,
    PublishedMessageT,
)
from superlinked.framework.queue.interface.queue_message import PayloadT, QueueMessage


class Queue(Generic[PayloadT, PublishedMessageT]):
    def __init__(
        self,
        message_converter: MessageConverter[PayloadT, PublishedMessageT],
        retry_timeout: int | None = None,
    ) -> None:
        self._message_converter = message_converter
        self._retry_timeout = retry_timeout

    @abstractmethod
    def publish(self, topic_name: str, message: QueueMessage[PayloadT]) -> None:
        pass
