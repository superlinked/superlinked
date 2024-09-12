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


from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.queue.interface.queue import Queue
from superlinked.framework.queue.interface.queue_message import QueueMessage
from superlinked.framework.queue.no_op_queue.no_op_message_converter import (
    NoOpMessageConverter,
)


class NoOpQueue(Queue[Any, Any]):
    def __init__(
        self,
    ) -> None:
        super().__init__(NoOpMessageConverter())

    @override
    def publish(self, topic_name: str, message: QueueMessage[Any]) -> None:
        pass
