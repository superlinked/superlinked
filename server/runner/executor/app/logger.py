import logging

from superlinked.framework.common.logging import LoggerConfigurator
from superlinked.framework.common.util.custom_structlog_processor import (
    CustomStructlogProcessor,
)

from executor.app.configuration.app_config import AppConfig


class ServerLoggerConfigurator:
    @staticmethod
    def setup_logger(app_config: AppConfig, logs_to_suppress: list[str] | None = None) -> None:
        processors = LoggerConfigurator._get_common_processors(app_config.EXPOSE_PII)  # noqa:SLF001 Private member
        processors += [CustomStructlogProcessor.drop_color_message_key]  # Drop color must be the last processor
        LoggerConfigurator.configure_structlog_logger(
            app_config.JSON_LOG_FILE, processors, app_config.EXPOSE_PII, app_config.LOG_AS_JSON
        )

        logging.getLogger("").setLevel(app_config.LOG_LEVEL)

        for _log in logs_to_suppress or []:
            logging.getLogger(_log).setLevel(logging.WARNING)

        # Disable uvicorn logging
        for _log in ["uvicorn", "uvicorn.error"]:
            logging.getLogger(_log).handlers.clear()
            logging.getLogger(_log).propagate = True

        logging.getLogger("uvicorn.access").handlers.clear()
        logging.getLogger("uvicorn.access").propagate = False
