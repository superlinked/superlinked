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
import logging
import os
import sys

import structlog
from beartype.typing import Any
from structlog.contextvars import merge_contextvars
from structlog.typing import EventDict, Processor, WrappedLogger

from superlinked.framework.common.settings import Settings

PACKAGE_NAME = "superlinked"
PII_PREFIX = "pii_"

settings = Settings()


class LoggerConfigurator:

    @staticmethod
    def configure_default_logger() -> None:
        if structlog.is_configured():
            return
        structlog.configure(
            processors=LoggerConfigurator._get_shared_processors()
            + LoggerConfigurator._get_stdlib_processors(),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @staticmethod
    def configure_structlog_logger(
        log_as_json: bool = settings.SUPERLINKED_LOG_AS_JSON,
        log_level: int | None = settings.SUPERLINKED_LOG_LEVEL,
        log_file_path: str | None = settings.SUPERLINKED_LOG_FILE_PATH,
    ) -> None:
        if log_level is None:
            log_level = logging.root.level

        # Set the stdlib logging config to enable structlog use
        logging.basicConfig(
            format="%(message)s", stream=sys.stdout, level=logging.root.level
        )

        # Applying log level ONLY to logs produced by the framework
        logging.getLogger(PACKAGE_NAME).setLevel(log_level)

        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            logger_factory=structlog.stdlib.LoggerFactory(),
            processors=LoggerConfigurator._get_structlog_processors(
                log_as_json, log_file_path
            ),
        )

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
        for k in list(event_dict.keys()):
            if k.startswith(PII_PREFIX):
                del event_dict[k]
        return event_dict

    @staticmethod
    def _get_structlog_processors(
        log_as_json: bool, log_file_path: str | None
    ) -> list[Processor]:
        json_file_processors = (
            [LoggerConfigurator._get_json_file_renderer(log_file_path)]
            if log_file_path is not None
            else []
        )
        console_processors: list[Processor] = (
            LoggerConfigurator._get_json_console_processors()
            if log_as_json
            else LoggerConfigurator._get_pretty_print_console_processors()
        )
        return (
            LoggerConfigurator._get_shared_processors()
            + json_file_processors
            + console_processors
        )

    @staticmethod
    def _get_shared_processors() -> list[Processor]:
        shared_processors: list[Processor] = [
            merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            LoggerConfigurator._set_log_var("process_id", os.getpid()),
            LoggerConfigurator._set_log_var("scope", PACKAGE_NAME),
            structlog.processors.format_exc_info,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.PositionalArgumentsFormatter(),
        ]
        if not settings.SUPERLINKED_EXPOSE_PII:
            shared_processors.append(LoggerConfigurator.filter_pii)
        return shared_processors

    @staticmethod
    def _get_pretty_print_console_processors() -> list[Processor]:
        return [structlog.dev.ConsoleRenderer()]

    @staticmethod
    def _get_json_console_processors() -> list[Processor]:
        """
        Print JSON when we run, e.g., in a Docker container.
        Also print structured tracebacks.
        """
        pii_sensitive_renderers: list[Processor] = (
            [structlog.processors.dict_tracebacks]
            if settings.SUPERLINKED_EXPOSE_PII
            else []
        )
        return pii_sensitive_renderers + [
            structlog.processors.EventRenamer("message"),  # renames event to message
            structlog.processors.JSONRenderer(),
        ]

    @staticmethod
    def _get_stdlib_processors() -> list[Processor]:
        return [structlog.stdlib.render_to_log_kwargs]
