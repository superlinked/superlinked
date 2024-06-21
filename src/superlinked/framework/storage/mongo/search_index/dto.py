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

from beartype.typing import Sequence
from pydantic import BaseModel


class IndexField(BaseModel):
    type: str
    path: str


class VectorIndexField(IndexField):
    numDimensions: int
    similarity: str


class CreateSearchIndexRequest(BaseModel):
    database: str
    collectionName: str
    name: str
    fields: Sequence[IndexField | VectorIndexField]
    type: str = "vectorSearch"


# Partial, full specification:
# https://www.mongodb.com/docs/atlas/reference/api-resources-spec/v2/#tag/Atlas-Search/operation/listAtlasSearchIndexes
class ListIndicesResponse(BaseModel):
    indexID: str
    name: str
