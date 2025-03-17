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

from collections.abc import Mapping

from beartype.typing import Sequence

from superlinked.framework.common.dag.context import (
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
)
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.dsl.query.query_weighting import QueryWeighting
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.query.dag.query_index_node import (
    QUERIED_SCHEMA_NAME_CONTEXT_KEY,
)
from superlinked.framework.query.query_dag_evaluator import QueryDagEvaluator
from superlinked.framework.query.query_node_input import QueryNodeInput

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryVectorFactory"] = False


class QueryVectorFactory:
    def __init__(self, dag: Dag) -> None:
        self._index_node_id = dag.index_node.node_id
        self._evaluator = QueryDagEvaluator(dag)
        self._query_weighting = QueryWeighting(dag)

    def produce_vector(
        self,
        query_node_inputs_by_node_id: Mapping[str, Sequence[QueryNodeInput]],
        global_space_weight_map: Mapping[Space, float],
        schema: IdSchemaObject,
        context_base: ExecutionContext,
    ) -> Vector:
        space_node_id_weight_map: dict[str, float] = self.__get_node_id_weight_map_from_space_weight_map(
            schema, global_space_weight_map
        )
        context = self._create_query_context(context_base, schema._schema_name, space_node_id_weight_map)
        result = self._evaluator.evaluate(query_node_inputs_by_node_id, context)
        return result

    def get_vector_parts(
        self, vectors: Sequence[Vector], node_ids: Sequence[str], schema: IdSchemaObject, context_base: ExecutionContext
    ) -> list[list[Vector]] | None:
        context = self._create_query_context(context_base, schema._schema_name)
        return self._evaluator.get_vector_parts(vectors, node_ids, context)

    def _create_query_context(
        self,
        context_base: ExecutionContext,
        schema_name: str,
        node_id_weight_map: dict[str, float] | None = None,
    ) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=context_base.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        if node_id_weight_map is not None:
            eval_context.update_data(self._query_weighting.get_node_weights(node_id_weight_map))
        eval_context.set_node_context_value(self._index_node_id, QUERIED_SCHEMA_NAME_CONTEXT_KEY, schema_name)
        return eval_context

    @staticmethod
    def __get_node_id_weight_map_from_space_weight_map(
        schema: IdSchemaObject, space_weight_map: Mapping[Space, float]
    ) -> dict[str, float]:
        return {space._get_embedding_node(schema).node_id: weight for space, weight in space_weight_map.items()}
