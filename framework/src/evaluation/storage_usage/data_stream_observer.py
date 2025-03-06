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
import tempfile
from dataclasses import dataclass
from functools import reduce

import pandas as pd
from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.observable import PublishedMessageT, Subscriber


@dataclass(frozen=True)
class FileInfo:
    size_bytes: int
    recognized_format: bool


class DataStreamObserver(Subscriber):
    def __init__(self) -> None:
        super().__init__()
        self.__observed_size_bytes = 0
        self.__immeasurable_messages_count = 0

    @property
    def observed_size_bytes(self) -> int:
        return self.__observed_size_bytes

    @property
    def immeasurable_messages_count(self) -> int:
        return self.__immeasurable_messages_count

    @override
    def update(self, messages: Sequence[PublishedMessageT]) -> None:
        if not messages:
            return
        file_info = [self.__get_file_info(message) for message in messages]
        sum_size_bytes, immeasurable_messages_count = reduce(
            lambda accumulator, element: (
                accumulator[0] + element.size_bytes,
                accumulator[1] + int(not element.recognized_format),
            ),
            file_info,
            (0, 0),
        )
        self.__observed_size_bytes += sum_size_bytes
        self.__immeasurable_messages_count += immeasurable_messages_count

    def reset(self) -> None:
        self.__observed_size_bytes = 0
        self.__immeasurable_messages_count = 0

    def __get_file_info(self, message: PublishedMessageT) -> FileInfo:
        # Currently we can only query the size of json or pandas.DataFrame inputs.
        file_size = 0
        recognized_format = True
        with tempfile.TemporaryFile(mode="w") as temp:
            if isinstance(message, pd.DataFrame):
                message.to_csv(temp, index=False)
            else:
                try:
                    json.dump(message, temp, ensure_ascii=True)
                except TypeError:
                    recognized_format = False
            file_size = temp.tell()
        return FileInfo(file_size, recognized_format)
