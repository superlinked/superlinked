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


from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema_object import SchemaField


class StorageNaming:
    INDEX_PREFIX = "idx_"
    NODE_DATA_PREFIX = "__node_data__"
    OBJECT_ID_INDEX_NAME = "__object_id__"
    ORIGIN_ID_INDEX_NAME = "__origin_id__"
    SCHEMA_INDEX_NAME = "__schema__"
    SCHEMA_FIELD_PREFIX = "__schema_field__"

    def get_index_name_from_node_id(self, node_id: str) -> str:
        return f"{StorageNaming.INDEX_PREFIX}{node_id}"

    def generate_field_name_from_schema_field(self, schema_field: SchemaField) -> str:
        if isinstance(schema_field, IdField):
            return StorageNaming.OBJECT_ID_INDEX_NAME
        return f"{StorageNaming.SCHEMA_FIELD_PREFIX}{schema_field.schema_obj._schema_name}_{schema_field.name}"

    def generate_node_data_field_name(self, node_id: str, node_data_key: str) -> str:
        return f"{StorageNaming.NODE_DATA_PREFIX}{node_id}_{node_data_key}"
