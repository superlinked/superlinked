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
        is_dev: bool = sys.stderr.isatty(),
        log_level: int | None = Settings().SUPERLINKED_LOG_LEVEL,
        log_file_path: str | None = Settings().LOG_FILE_PATH,
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
                is_dev, log_file_path
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
    def add_json_file_renderer(path: str) -> Processor:
        def render_to_json_file(
            _: WrappedLogger, __: str, event_dict: EventDict
        ) -> EventDict:
            line = json.dumps(event_dict)
            with open(path, "a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
            return event_dict

        return render_to_json_file

    @staticmethod
    def _get_structlog_processors(
        is_dev: bool, log_file_path: str | None
    ) -> list[Processor]:
        additional_processors = (
            [LoggerConfigurator.add_json_file_renderer(log_file_path)]
            if log_file_path is not None
            else []
        )
        env_based_processors: list[Processor] = (
            LoggerConfigurator._get_dev_processors()
            if is_dev
            else LoggerConfigurator._get_prod_processors()
        )
        return (
            LoggerConfigurator._get_shared_processors()
            + additional_processors
            + env_based_processors
        )

    @staticmethod
    def _get_shared_processors() -> list[Processor]:
        return [
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

    @staticmethod
    def _get_dev_processors() -> list[Processor]:
        """Pretty printing when we run in a terminal session."""
        return [structlog.dev.ConsoleRenderer()]

    @staticmethod
    def _get_prod_processors() -> list[Processor]:
        """
        Print JSON when we run, e.g., in a Docker container.
        Also print structured tracebacks.
        """
        return [
            structlog.processors.dict_tracebacks,
            structlog.processors.EventRenamer("message"),  # renames event to message
            structlog.processors.JSONRenderer(),
        ]

    @staticmethod
    def _get_stdlib_processors() -> list[Processor]:
        return [structlog.stdlib.render_to_log_kwargs]
