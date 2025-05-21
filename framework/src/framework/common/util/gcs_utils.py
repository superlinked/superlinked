# Copyright 2025 Superlinked, Inc
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
from dataclasses import dataclass

from beartype.typing import cast
from deprecated import deprecated
from google.api_core import exceptions, retry
from google.auth.credentials import Credentials
from google.cloud import storage


@dataclass
class GcsClientParams:
    credentials: Credentials
    project: str


class GCSFileOps:
    cached_params: GcsClientParams | None = None

    def __init__(self, client_params: GcsClientParams | None = None):
        self.init_single()
        self.__client_params = client_params or self.cached_params
        self.__storage_client: storage.Client | None = None

    @classmethod
    def init_single(cls) -> None:
        if cls.cached_params is None:
            client = storage.Client()
            cls.cached_params = GcsClientParams(credentials=client._credentials, project=client.project)

    @property
    def storage_client(self) -> storage.Client:
        if self.__storage_client is not None:
            return cast(storage.Client, self.__storage_client)
        client = storage.Client(
            project=(self.__client_params.project if self.__client_params is not None else None),
            credentials=(self.__client_params.credentials if self.__client_params is not None else None),
        )
        self.__storage_client = client
        return client

    def object_exists(self, uri: str) -> bool:
        blob = storage.Blob.from_string(uri, self.storage_client)
        return blob.exists()

    @retry.Retry(
        predicate=retry.if_exception_type(exceptions.ServiceUnavailable, exceptions.InternalServerError),
        initial=1.0,
        maximum=60.0,
        multiplier=2.0,
        deadline=300.0,
    )
    def copy_object(self, src_uri: str, dst_uri: str) -> None:
        src_blob = storage.Blob.from_string(src_uri, self.storage_client)
        src_bucket = src_blob.bucket
        dst_blob = storage.Blob.from_string(dst_uri, self.storage_client)
        dst_bucket = dst_blob.bucket
        src_bucket.copy_blob(src_blob, dst_bucket, dst_blob.name)


@deprecated("Use GCSFileOps")
def object_exists(uri: str) -> bool:
    return GCSFileOps().object_exists(uri)


@deprecated("Use GCSFileOps")
def copy_object(src_uri: str, dst_uri: str) -> None:
    return GCSFileOps().copy_object(src_uri, dst_uri)
