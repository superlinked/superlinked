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

import re
from dataclasses import dataclass
from enum import Enum

import structlog

logger = structlog.getLogger(__name__)


class StorageType(Enum):
    S3 = "s3"
    GCS = "gcs"
    LOCAL = "local"


@dataclass
class AppLocation:
    type_: StorageType
    bucket: str | None
    path: str


class AppLocationParser:
    def _get_bucket_and_path_or_raise(self, pattern: str, app_location: str) -> tuple[str, str]:
        match = re.search(pattern, app_location)
        if not match:
            msg = f"Invalid location format {app_location}"
            raise ValueError(msg)
        try:
            bucket, path = match.groups()
        except ValueError as e:
            msg = f"Expected bucket and path in {app_location}"
            raise ValueError(msg) from e
        return bucket, path

    def parse(self, app_location: str) -> AppLocation:
        """
        Parse the application location URL to extract the storage type, bucket, and path.
        """
        bucket: str | None
        pattern: str

        match app_location:
            case app_location if app_location.startswith(("s3://", "s3a://", "s3n://")):
                type_ = StorageType.S3
                pattern = r"s3[a|n]?://([^/^\n]+)/?(.*)"
                bucket, path = self._get_bucket_and_path_or_raise(pattern, app_location)
            case app_location if "amazonaws.com" in app_location:
                # Handle both AWS S3 URL formats
                if re.match(r"https?://[a-z0-9-]+\.s3\.?[a-z0-9-]*\.amazonaws\.com/.+", app_location):
                    pattern = r"https?://([^/.]+)\.s3\.?[a-z0-9-]*\.amazonaws\.com/(.+)"
                else:
                    pattern = r"https?://s3\.[a-z0-9-]+\.amazonaws\.com/([^/]+)/(.+)"
                type_ = StorageType.S3
                bucket, path = self._get_bucket_and_path_or_raise(pattern, app_location)
            case app_location if "storage.googleapis.com" in app_location or "storage.cloud.google.com" in app_location:
                type_ = StorageType.GCS
                pattern = r"https?://(?:storage\.cloud\.google\.com|storage\.googleapis\.com)/([^/]+)/(.+)"
                bucket, path = self._get_bucket_and_path_or_raise(pattern, app_location)
            case app_location if app_location.startswith("gs://"):
                type_ = StorageType.GCS
                pattern = r"gs://([^/]+)/(.+)"
                bucket, path = self._get_bucket_and_path_or_raise(pattern, app_location)
            case app_location if app_location == "local":
                type_ = StorageType.LOCAL
                bucket = None
                path = "/src"
            case app_location if app_location.startswith("/"):
                type_ = StorageType.LOCAL
                bucket = None
                path = app_location
            case _:
                msg = "Unsupported storage location"
                raise ValueError(msg)
        logger.info("parsed app location", app_type=type_, bucket=bucket, path=path)
        return AppLocation(type_=type_, bucket=bucket, path=path)
