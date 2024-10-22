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

from hashlib import md5


class BlobIdGenerator:
    @staticmethod
    def generate_id(schema_id: str, object_id: str, field_name: str) -> str:
        input_string = f"{schema_id}:{object_id}:{field_name}".encode("utf-8")
        return md5(input_string).hexdigest()

    @staticmethod
    def generate_id_with_path(schema_id: str, object_id: str, field_name: str) -> str:
        blob_id = BlobIdGenerator.generate_id(schema_id, object_id, field_name)
        directory_structure = f"{blob_id[0]}/{blob_id[1]}/{blob_id[2]}"
        return f"{directory_structure}/{blob_id}"
