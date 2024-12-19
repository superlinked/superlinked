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

from dataclasses import dataclass

from beartype.typing import Generic, Sequence, cast
from typing_extensions import override

from superlinked.framework.common.observable import Subscriber
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.util import time_util
from superlinked.framework.queue.interface.queue import Queue
from superlinked.framework.queue.interface.queue_message import (
    MessageBody,
    PayloadT,
    QueueMessage,
)


@dataclass(frozen=True)
class SchemaIdMessageBody(Generic[PayloadT], MessageBody[PayloadT]):
    schema_id: str


class QueueSubscriber(Generic[PayloadT], Subscriber[PayloadT]):
    def __init__(
        self,
        queue: Queue[SchemaIdMessageBody[PayloadT]],
        schema_id: str,
        topic_name: str | None,
        message_type: str,
    ) -> None:
        super().__init__()
        self.__queue = queue
        self.__schema_id = schema_id
        self.__topic_name = topic_name
        self.__message_type = message_type
        self.__queue_message_version = Settings().QUEUE_MESSAGE_VERSION

    @override
    def update(self, messages: Sequence[PayloadT]) -> None:
        if self.__topic_name is not None:
            for item in messages:
                if isinstance(item, dict):
                    message = self.__generate_queue_message(item)
                    self.__queue.publish(self.__topic_name, message)

    def __generate_queue_message(self, payload: dict) -> QueueMessage[SchemaIdMessageBody[PayloadT]]:
        format_ = payload.__class__.__name__
        created_at = time_util.now()
        return QueueMessage(
            type_=self.__message_type,
            format_=format_,
            created_at=created_at,
            version=self.__queue_message_version,
            message=SchemaIdMessageBody(cast(PayloadT, payload), self.__schema_id),
        )
