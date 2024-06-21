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


from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    DagEvaluationException,
    InvalidSchemaException,
)
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.evaluator.online_dag_evaluator import OnlineDagEvaluator
from superlinked.framework.online.dag.evaluation_result import EvaluationResult


class QueryDagEvaluator(OnlineDagEvaluator):
    def evaluate_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        result = super().evaluate([parsed_schema], context)[0]
        QueryDagEvaluator.__check_evaluation(result)
        return result

    @staticmethod
    def __check_evaluation(evaluation: EvaluationResult[Vector]) -> None:
        if len(evaluation.chunks) > 0:
            raise DagEvaluationException(
                "Evaluation cannot have chunked parts in query context."
            )

    def re_weight_vector(
        self,
        schema: SchemaObject,
        vector: Vector,
        context: ExecutionContext,
    ) -> Vector:
        if (
            online_schema_dag := self._schema_online_schema_dag_mapper.get(schema)
        ) is not None:
            return online_schema_dag.leaf_node._re_weight_vector(
                schema, vector, context
            )
        raise InvalidSchemaException(
            f"Schema ({schema._schema_name}) isn't present in the index."
        )
