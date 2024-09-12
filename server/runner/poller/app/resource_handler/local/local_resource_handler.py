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
import shutil
from datetime import datetime, timezone

import structlog

from poller.app.resource_handler.resource_handler import ResourceHandler

logger = structlog.getLogger(__name__)


class LocalResourceHandler(ResourceHandler):
    def get_bucket(self) -> str:
        return "local"

    def _download_file(self, _: str | None, object_name: str, download_path: str) -> None:
        shutil.copy(object_name, download_path)

    def poll(self) -> None:
        if not os.path.exists(self.app_location.path):
            logger.error("path does not exist", path=self.app_location.path)
            return

        notification_needed = False
        for root, _, files in os.walk(self.app_location.path):
            for file in files:
                file_path = os.path.join(root, file)
                notification_needed |= self._process_file(file_path)
        if notification_needed:
            self.notify_executor()

    def _process_file(self, file_path: str) -> bool:
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
        file_changed = False
        try:
            if self.is_object_outdated(file_time, file_path):
                destination_path = self.get_destination_path(file_path)
                self.download_file(self.get_bucket(), file_path, destination_path)
                logger.info("downloaded file", source=file_path, destination=destination_path)
                file_changed = True
        except (FileNotFoundError, PermissionError):
            logger.exception("failed to download file", path=file_path)
        return file_changed
