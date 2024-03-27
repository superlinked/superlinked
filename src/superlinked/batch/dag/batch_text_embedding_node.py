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

import numpy as np
from pyspark.sql import DataFrame
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, FloatType
from sentence_transformers import SentenceTransformer

from superlinked.batch.dag.batch_node import BatchNode
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode


class BatchTextEmbeddingNode(BatchNode[TextEmbeddingNode]):
    """
    Class for creating TextEmbedding in Spark.

    """

    def __init__(self, node: TextEmbeddingNode) -> None:
        self.model = SentenceTransformer(node.model_name)
        self.__length = self.model.get_sentence_embedding_dimension()
        self.input_column = node.parents[0].node_id
        self.result_column = node.node_id

    # TODO: https://linear.app/superlinked/issue/ENG-1513/add-spark-vector-type-to-batch-module
    def transform(self, df: DataFrame) -> DataFrame:
        model = self.model
        encode_udf = udf(
            lambda x: model.encode(x).astype(np.float32).tolist(),
            ArrayType(FloatType()),
        )
        df = df.withColumn(self.result_column, encode_udf(self.input_column))
        return df

    @property
    def length(self) -> int:
        return self.__length
