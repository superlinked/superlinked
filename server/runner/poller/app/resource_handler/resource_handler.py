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

import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests
import structlog

from poller.app.app_location_parser.app_location_parser import AppLocation
from poller.app.config.poller_config import PollerConfig

logger = structlog.getLogger(__name__)


class ResourceHandler(ABC):
    def __init__(self, app_location: AppLocation) -> None:
        self.app_location = app_location
        self.poller_config = PollerConfig()

    @abstractmethod
    def poll(self) -> None:
        pass

    def download_file(self, bucket_name: str, object_name: str, download_path: str) -> None:
        logger.info("copied file", source=object_name, destination=download_path)
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        self._download_file(bucket_name, object_name, download_path)

    @abstractmethod
    def _download_file(self, bucket_name: str, object_name: str, download_path: str) -> None:
        pass

    def get_bucket(self) -> str:
        if self.app_location.bucket is None:
            msg = "Bucket name is None"
            raise ValueError(msg)
        return self.app_location.bucket

    def convert_to_utc(self, dt: datetime) -> datetime:
        """
        Convert a datetime object to UTC timezone.
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def is_object_outdated(self, object_time: datetime, object_name: str) -> bool:
        return self.convert_to_utc(object_time) > self.__get_local_file_last_modified_date(object_name)

    def get_destination_path(self, object_name: str) -> str:
        return os.path.join(self.poller_config.download_location, object_name)

    def __get_local_file_last_modified_date(self, object_name: str) -> datetime:
        path = self.get_destination_path(os.path.basename(object_name))
        if not os.path.exists(path):
            return datetime.fromtimestamp(0, tz=timezone.utc)
        return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)

    def notify_executor(self) -> None:
        """
        Notify the executor API about the new version by making a PUT request to /reload.
        """
        api_url = f"{self.poller_config.executor_url}:{self.poller_config.executor_port}/reload"
        response = None
        try:
            response = requests.post(api_url, timeout=10)
            response.raise_for_status()
            logger.info("notified executor", notification_event="file_change", url=api_url)
        except requests.HTTPError:
            logger.exception("failed to notify executor", notification_event="file_change", url=api_url)
        except requests.RequestException:
            logger.exception("failed to notify executor", notification_event="file_change", url=api_url)

    def check_api_health(self) -> bool:
        """
        Check the health of the API and return True if it's healthy, False otherwise.
        Retries the request up to 10 times with a 5-second delay between attempts.
        """
        api_endpoint = f"{self.poller_config.executor_url}:{self.poller_config.executor_port}/health"
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.get(api_endpoint, timeout=5)
                response.raise_for_status()
                return True  # noqa: TRY300
            except (requests.HTTPError, requests.RequestException) as e:  # noqa: PERF203
                logger.warning(
                    "executor is unreachable, possibly starting up",
                    reason=str(e),
                    status_code=getattr(e.response, "status_code", "No status code available"),
                    attempt=attempt + 1,
                    max_retries=max_retries,
                )
                time.sleep(5)
        return False
