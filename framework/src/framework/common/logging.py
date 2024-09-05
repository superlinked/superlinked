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

import logging
import os

import structlog
from beartype.typing import cast
from structlog.contextvars import merge_contextvars
from structlog.typing import Processor

from superlinked.framework.common.settings import Settings
from superlinked.framework.common.util.custom_structlog_processor import (
    CustomStructlogProcessor,
)

PACKAGE_NAME = "superlinked"

settings = Settings()


class LoggerConfigurator:

    @staticmethod
    def configure_default_logger() -> None:
        if structlog.is_configured():
            return
        structlog.configure(
            processors=LoggerConfigurator._get_common_processors()
            + [structlog.stdlib.render_to_log_kwargs],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @staticmethod
    def configure_structlog_logger(
        log_as_json: bool = settings.SUPERLINKED_LOG_AS_JSON,
        log_file_path: str | None = settings.SUPERLINKED_LOG_FILE_PATH,
        additional_processors: list[Processor] | None = None,
    ) -> None:
        if additional_processors is None:
            additional_processors = []

        shared_processors: list[Processor] = additional_processors + (
            LoggerConfigurator._get_structlog_processors(log_as_json, log_file_path)
        )

        structlog.configure(
            processors=shared_processors
            + [
                # Prepare event dict for `ProcessorFormatter`.
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        LoggerConfigurator._format_standard_logs_with_structlog(
            log_as_json, shared_processors
        )

    @staticmethod
    def _format_standard_logs_with_structlog(
        log_as_json: bool, shared_processors: list[Processor]
    ) -> None:
        log_renderer: Processor = cast(
            Processor,
            (
                structlog.processors.JSONRenderer()
                if log_as_json
                else structlog.dev.ConsoleRenderer()
            ),
        )
        stdlib_processors: list[Processor] = [
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ]
        formatter = structlog.stdlib.ProcessorFormatter(
            # These run ONLY on `logging` entries that do NOT originate within structlog.
            foreign_pre_chain=shared_processors,
            # These run on ALL entries after the pre_chain is done.
            processors=stdlib_processors,
        )
        # Use OUR `ProcessorFormatter` to format all `logging` entries.
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    @staticmethod
    def _get_structlog_processors(
        log_as_json: bool, log_file_path: str | None
    ) -> list[Processor]:
        json_file_processors: list[Processor] = (
            [CustomStructlogProcessor._get_json_file_renderer(log_file_path)]
            if log_file_path is not None
            else []
        )
        json_console_processors: list[Processor] = (
            [
                structlog.processors.EventRenamer("message"),
                structlog.processors.format_exc_info,
            ]
            if log_as_json
            else []
        )
        return (
            LoggerConfigurator._get_common_processors()
            + json_file_processors
            + json_console_processors
        )

    @staticmethod
    def _get_common_processors() -> list[Processor]:
        shared_processors: list[Processor] = [
            merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            structlog.processors.TimeStamper(fmt="iso"),
            CustomStructlogProcessor._set_log_var("process_id", os.getpid()),
            CustomStructlogProcessor._set_log_var("scope", PACKAGE_NAME),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]
        if not settings.SUPERLINKED_EXPOSE_PII:
            shared_processors.append(CustomStructlogProcessor.filter_pii)
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
