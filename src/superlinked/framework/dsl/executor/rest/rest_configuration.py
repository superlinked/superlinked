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

from dataclasses import dataclass

from pydantic import model_validator

from superlinked.framework.common.util.immutable_model import ImmutableBaseModel
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.query.query import QueryObj


class RestEndpointConfiguration(ImmutableBaseModel):
    query_path_prefix: str = "search"
    ingest_path_prefix: str = "ingest"
    api_root_path: str = "/api/v1"

    @model_validator(mode="before")
    def add_slash_to_api_root_path(cls, values: dict) -> dict:
        api_root_path = values.get("api_root_path")
        if api_root_path and not api_root_path.startswith("/"):
            values["api_root_path"] = "/" + api_root_path
        return values


@dataclass(frozen=True)
class RestQuery:
    rest_descriptor: RestDescriptor
    query_obj: QueryObj

    @property
    def path(self) -> str | None:
        return self.rest_descriptor.query_path
