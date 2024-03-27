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

from pyspark.sql import DataFrame
from pyspark.sql.functions import column

from superlinked.batch.dag.batch_node import BatchNode
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode


class BatchSchemaFieldNode(BatchNode[SchemaFieldNode]):
    def __init__(self, node: SchemaFieldNode) -> None:
        self.input_field = node.schema_field.name
        self.node_id = node.node_id

    def transform(self, df: DataFrame) -> DataFrame:
        return df.withColumn(self.node_id, column(self.input_field))
