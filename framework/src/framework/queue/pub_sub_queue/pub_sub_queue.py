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


import json
from dataclasses import asdict

import requests
import structlog
from beartype.typing import Any, Generic, Sequence
from google.api_core import exceptions as core_exceptions
from google.api_core import retry as retries
from google.cloud import pubsub_v1  # type: ignore
from typing_extensions import override

from superlinked.framework.queue.interface.queue import Queue
from superlinked.framework.queue.interface.queue_message import MessageT, QueueMessage

# The metaclass of these are overwritten that's the reason behind the use of Any.
EXCEPTIONS_TO_RETRY: Sequence[Any] = [
    core_exceptions.Aborted,
    core_exceptions.DeadlineExceeded,
    core_exceptions.InternalServerError,
    core_exceptions.ResourceExhausted,
    core_exceptions.ServiceUnavailable,
    core_exceptions.Unknown,
    core_exceptions.Cancelled,
    requests.exceptions.ConnectionError,
]

logger = structlog.getLogger()


def on_error(exception: Exception) -> None:
    logger.exception(exception)


def on_publish_done(future: pubsub_v1.publisher.futures.Future) -> None:
    try:
        message_id = future.result()
        logger.debug(
            "published message",
            message_id=message_id,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception(
            "failed to publish",
            error_type=type(e).__name__,
            error_details=str(e),
        )


class PubSubQueue(Queue[MessageT], Generic[MessageT]):
    DEFAULT_TIMEOUT = 60.0

    def __init__(
        self,
        project_id: str,
        retry_timeout: int | None = None,
    ) -> None:
        super().__init__(retry_timeout)
        self._project_id = project_id
        self._publisher = pubsub_v1.PublisherClient()
        self._retry = self.__init_retry()

    def __init_retry(self) -> retries.Retry:
        return retries.Retry(
            timeout=(
                float(self._retry_timeout)
                if self._retry_timeout is not None
                else PubSubQueue.DEFAULT_TIMEOUT
            ),
            predicate=retries.if_exception_type(*EXCEPTIONS_TO_RETRY),
            on_error=on_error,
        )

    @override
    def publish(self, topic_name: str, message: QueueMessage[MessageT]) -> None:
        topic_path = self._publisher.topic_path(self._project_id, topic_name)

        future = self._publisher.publish(
            topic_path,
            data=self._message_to_bytes(message),
            retry=self._retry,
        )
        future.add_done_callback(on_publish_done)

    def _message_to_bytes(self, message: QueueMessage[MessageT]) -> bytes:
        message_dict = asdict(message)
        return json.dumps(message_dict).encode("utf-8")
