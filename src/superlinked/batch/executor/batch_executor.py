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

from typing import Mapping, cast

from pyspark.sql import DataFrame, SparkSession

from superlinked.batch.dag.batch_node import BatchNode
from superlinked.batch.dag.batch_schema_field_node import BatchSchemaFieldNode
from superlinked.batch.dag.batch_text_embedding_node import BatchTextEmbeddingNode
from superlinked.batch.dag.dummy_batch_node import DummyBatchNode
from superlinked.batch.source.batch_source import BatchSource
from superlinked.batch.writer.dataframe_writer import DataFrameWriter
from superlinked.framework.common.dag.context import (
    ContextValue,
    ExecutionContext,
    ExecutionEnvironment,
)
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode
from superlinked.framework.common.schema.schema_object import SchemaObjectT
from superlinked.framework.dsl.executor.executor import App, Executor
from superlinked.framework.dsl.index.index import Index


class BatchExecutor(Executor[BatchSource]):
    """
    Batch Executor. Creates a Spark Session and constructs a batch dag by mapping Nodes to BatchNodes.
    Creates a BatchApp with the indices and their values.

    """

    def __init__(
        self,
        sources: list[BatchSource],
        indices: list[Index],
        context_data: Mapping[str, Mapping[str, ContextValue]] | None = None,
        df_writer: DataFrameWriter = DataFrameWriter(),
    ):
        """
        Initialize the BatchExecutor.

        Args:
            sources (list[BatchSource]): List of batch sources.
            indices (list[Index]): List of indices.
            context (Mapping[str, Mapping[str, Any]]): Context mapping.
            df_writer: DataFrameWriter object for writing output.
        """
        super().__init__(
            sources,
            indices,
            ExecutionContext.from_context_data(
                context_data, environment=ExecutionEnvironment.IN_MEMORY
            ),
        )

        self.__spark_session: SparkSession | None = None
        self.node_mapping = {
            TextEmbeddingNode: BatchTextEmbeddingNode,
            SchemaFieldNode: BatchSchemaFieldNode,
            IndexNode: DummyBatchNode,
        }
        self.source_mapping = {source.schema: source for source in sources}
        self.index_nodes = indices
        self.df_writer = df_writer

    @property
    def spark_session(self) -> SparkSession:
        if not self.__spark_session:
            self.__spark_session = SparkSession.builder.appName(
                "batch_executor"
            ).getOrCreate()
        return self.__spark_session

    def _get_source_by_schema(self, schema_: SchemaObjectT) -> BatchSource:
        """
        Return BatchSource object corresponding to input SchemaObject.

        return: BatchSource object
        """
        return self.source_mapping[schema_]

    def map_to_batch_nodes(self, nodes: list[Node]) -> Mapping[Node, BatchNode]:
        """
        Take a list of input nodes and create a mapping between the Node and its BatchNode pair.

        return: Mapping of Node to BatchNode
        """
        batch_nodes = {
            node: self.node_mapping[type(node)](node)
            for node in nodes
            if type(node) in self.node_mapping
        }

        return batch_nodes

    def __create_df(
        self, spark_session: SparkSession, source: BatchSource
    ) -> DataFrame:
        """
        Create spark df from initial input data.

        return: Spark DataFrame
        """
        return spark_session.read.schema(source.spark_schema).json(source.path)

    def run(self) -> BatchApp:
        """
        Run executor, transform nodes into BatchNodes and evaluate nodes.

        Returns:
            BatchApp instance initialized with an index to dataframe mapping.
        """
        index_to_df: dict[Index, DataFrame] = {}
        for index in self._indices:
            dag = index._dag
            batch_nodes = self.map_to_batch_nodes(dag.nodes)
            dataframes_by_schema = {
                schema: self.__create_df(
                    self.spark_session, self.source_mapping[schema]
                )
                for schema in dag.schemas
            }
            schema_by_batch_field_node = {
                batch_node: cast(SchemaFieldNode, node).schema_field.schema_obj
                for node, batch_node in batch_nodes.items()
                if isinstance(batch_node, BatchSchemaFieldNode)
            }
            current_node: Node = index._node
            node_path: list[BatchNode] = []
            while True:
                node_path.append(batch_nodes[current_node])
                if len(current_node.parents) > 0:
                    current_node = current_node.parents[0]
                else:
                    break
            node_path.reverse()
            batch_field_node = cast(BatchSchemaFieldNode, node_path[0])
            current_df = dataframes_by_schema[
                schema_by_batch_field_node[batch_field_node]
            ]
            current_df = batch_field_node.transform(current_df)
            for batch_node in node_path[1:]:
                current_df = batch_node.transform(current_df)
            index_to_df[index] = current_df

        return BatchApp(self, index_to_df, self.df_writer)


class BatchApp(App[BatchExecutor]):
    """
    Batch App class. Wrapper around the spark session.

    Attributes:
        executor (BatchExecutor): An instance of BatchExecutor.
    """

    def __init__(
        self,
        executor: BatchExecutor,
        index_to_df: Mapping[Index, DataFrame],
        df_writer: DataFrameWriter,
    ):
        """
        Initialize the BatchApp (spark app) from an BatchExecutor.

        Args:
            index_to_df:
            app: running spark session
        """
        self.index_to_df = index_to_df
        self.app = executor.spark_session
        for index, df in index_to_df.items():
            df_writer.df_name = index._node_id
            df_writer.write_data(df)

    def stop(self) -> None:
        """
        Stop SparkSession.
        """
        self.app.stop()
