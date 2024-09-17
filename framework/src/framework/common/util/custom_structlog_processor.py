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

from beartype.typing import Any
from structlog.typing import EventDict, Processor, WrappedLogger

PII_PREFIX = "pii_"


class CustomStructlogProcessor:

    @staticmethod
    def _set_log_var(key: str, value: Any, override: bool = False) -> Processor:
        def set_event_arg(
            _: WrappedLogger, __: str, event_dict: EventDict
        ) -> EventDict:
            if override or key not in event_dict:
                event_dict[key] = value
            return event_dict

        return set_event_arg

    @staticmethod
    def drop_color_message_key(
        _: WrappedLogger, __: str, event_dict: EventDict
    ) -> EventDict:
        """
        Uvicorn logs the message a second time in the extra `color_message`, but we don't
        need it. This processor drops the key from the event dict if it exists.
        """
        event_dict.pop("color_message", None)
        return event_dict

    @staticmethod
    def _get_json_file_renderer(log_file_path: str) -> Processor:
        def render_to_json_file(
            _: WrappedLogger, __: str, event_dict: EventDict
        ) -> EventDict:
            line = json.dumps(event_dict)
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
            return event_dict

        return render_to_json_file

    @staticmethod
    def filter_pii(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
        event_dict = {
            k: v for k, v in event_dict.items() if not k.startswith(PII_PREFIX)
        }
        return event_dict

    @staticmethod
    def evaluate_lazy_arguments(
        _: WrappedLogger, __: str, event_dict: EventDict
    ) -> EventDict:
        for key, value in event_dict.items():
            if callable(value):
                event_dict[key] = value()
        return event_dict
