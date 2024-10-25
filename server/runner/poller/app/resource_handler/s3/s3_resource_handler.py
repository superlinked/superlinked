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
import os

import boto3
import structlog
from botocore.client import Config
from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client

from poller.app.app_location_parser.app_location_parser import AppLocation
from poller.app.resource_handler.resource_handler import ResourceHandler

logger = structlog.getLogger(__name__)


class S3ResourceHandler(ResourceHandler):
    def __init__(
        self,
        app_location: AppLocation,
        client: S3Client | None = None,
    ) -> None:  # client=None for easier testability
        super().__init__(app_location)
        self.client = client or self.initialize_s3_client()
        self.resource = boto3.resource("s3")

    def initialize_s3_client(self) -> S3Client:
        """
        Initialize the S3 client, with fallback to credentials file if necessary.
        """
        try:
            # First, try to create an S3 resource without explicit credentials
            client = boto3.client("s3", config=Config(signature_version="s3v4"))
            if self.app_location.bucket is not None:
                client.head_bucket(Bucket=self.app_location.bucket)  # Test access
        except ClientError:
            # If the first method fails, try to use credentials from a JSON file
            try:
                with open(self.poller_config.aws_credentials, encoding="utf-8") as aws_cred_file:
                    aws_credentials = json.load(aws_cred_file)
                return boto3.client(
                    "s3",
                    aws_access_key_id=aws_credentials["aws_access_key_id"],
                    aws_secret_access_key=aws_credentials["aws_secret_access_key"],
                    region_name=aws_credentials["region"],
                )
            except FileNotFoundError as e:
                msg = "Could not find AWS credentials file and no IAM role available."
                raise FileNotFoundError(msg) from e
        else:
            return client

    def poll(self) -> None:
        notification_needed = False
        bucket_name = self.get_bucket()
        bucket = self.resource.Bucket(bucket_name)
        for obj in bucket.objects.filter(Prefix=self.app_location.path):
            file_name = os.path.basename(obj.key)
            if file_name not in self.poller_config.allowed_files:
                logger.debug("skipped file", filename=file_name, allowed_files=self.poller_config.allowed_files)
                continue
            if self.is_object_outdated(obj.last_modified, obj.key):
                self.download_file(bucket_name, obj.key, self.get_destination_path(file_name))
                notification_needed = True

        if notification_needed:
            self.notify_executor()

    def _download_file(self, bucket_name: str, object_name: str, download_path: str) -> None:
        self.client.download_file(Bucket=bucket_name, Key=object_name, Filename=download_path)
