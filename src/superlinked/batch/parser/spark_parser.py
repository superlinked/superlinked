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

from __future__ import annotations

from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from superlinked.framework.common.schema.id_schema_object import SchemaObject
from superlinked.framework.common.schema.schema_object import (
    Float,
    Integer,
    String,
    Timestamp,
)


class SchemaMapper:
    """
    SchemaMapper gets a source schema and maps it to a Spark schema.
    """

    # TODO: On init, read all SchemaField types and check if they have a mapping
    def __init__(
        self,
        schema: SchemaObject,
    ) -> None:
        self.schema = schema
        self.mapping = {
            String: StringType,
            Timestamp: TimestampType,
            Float: FloatType,
            Integer: IntegerType,
        }

    def map_schema(self) -> StructType:
        """
        Generate spark schema from mapping
        return: spark_schema
        """
        struct_fields = list(
            StructField(field.name, self.mapping[type(field)](), True)
            for field in self.schema._get_schema_fields()
            if type(field) in self.mapping
        )

        spark_schema = StructType(struct_fields)
        return spark_schema
