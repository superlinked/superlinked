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

import configparser
import logging

from poller.app.logging import LoggerConfigurator


# pylint: disable=too-many-instance-attributes
class PollerConfig:
    is_logger_configured = False

    def __init__(self) -> None:
        poller_dir = "poller"
        poller_config_path = f"{poller_dir}/poller_config.ini"

        config = configparser.ConfigParser()
        config.read(poller_config_path)

        self.poll_interval_seconds = config.getint("POLLER", "POLL_INTERVAL_SECONDS")
        self.executor_port = config.getint("POLLER", "EXECUTOR_PORT")
        self.executor_url = config.get("POLLER", "EXECUTOR_URL")
        self.aws_credentials = config.get("POLLER", "AWS_CREDENTIALS")
        self.gcp_credentials = config.get("POLLER", "GCP_CREDENTIALS")
        self.download_location = config.get("POLLER", "DOWNLOAD_LOCATION")
        self.log_level = config.get("POLLER", "LOG_LEVEL")
        self.json_log_file = config.get("POLLER", "JSON_LOG_FILE", fallback=None)
        self.log_as_json = config.get("POLLER", "LOG_AS_JSON", fallback="false").lower() == "true"
        self._setup_logger()

    def _setup_logger(self) -> None:
        # structlog.is_configured works incorrectly so use a local state
        if PollerConfig.is_logger_configured:
            return
        LoggerConfigurator.configure_structlog_logger(self.json_log_file, log_as_json=self.log_as_json)
        configured_logger = logging.getLogger("")
        configured_logger.setLevel(self.log_level.upper())
        PollerConfig.is_logger_configured = True
