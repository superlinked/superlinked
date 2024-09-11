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
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests

from poller.app.app_location_parser.app_location_parser import AppLocation
from poller.app.config.poller_config import PollerConfig

logger = logging.getLogger(__name__)


class ResourceHandler(ABC):
    def __init__(self, app_location: AppLocation) -> None:
        self.app_location = app_location
        self.poller_config = PollerConfig()

    @abstractmethod
    def poll(self) -> None:
        pass

    def download_file(self, bucket_name: str, object_name: str, download_path: str) -> None:
        logger.info("Copy file from %s to %s", object_name, download_path)
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
        filename = os.path.basename(object_name.lstrip("/"))
        return os.path.join(self.poller_config.download_location, filename)

    def __get_local_file_last_modified_date(self, object_name: str) -> datetime:
        path = self.get_destination_path(object_name)
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
            logger.info("Executor successfully notified of file change.")
        except requests.HTTPError:
            logger.exception(
                "Notification of file change failed with HTTP status code: %s",
                response.status_code if response else "No response received.",
            )
        except requests.RequestException:
            logger.exception("Notification of file change failed due to a network-related error.")

    def check_api_health(self, *, verbose: bool = True) -> bool:
        """
        Check the health of the API and return True if it's healthy, False otherwise.
        """
        api_endpoint = f"{self.poller_config.executor_url}:{self.poller_config.executor_port}/health"
        try:
            response = requests.get(api_endpoint, timeout=5)
            response.raise_for_status()
        except (requests.HTTPError, requests.RequestException) as e:
            if verbose:
                logger.warning("Executor is unreachable, possibly restarting. Reason: %s.", e)
            return False
        return True
