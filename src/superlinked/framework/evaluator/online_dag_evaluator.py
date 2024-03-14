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
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidDagEffectException,
    InvalidSchemaException,
)
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.compiler.online_schema_dag_compiler import (
    OnlineSchemaDagCompiler,
)
from superlinked.framework.evaluator.dag_evaluator import DagEvaluator
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_schema_dag import OnlineSchemaDag
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)
from superlinked.framework.storage.entity_store_manager import EntityStoreManager


class OnlineDagEvaluator(DagEvaluator[EvaluationResult[Vector]]):
    def __init__(
        self,
        dag: Dag,
        schemas: set[SchemaObject],
        entity_store_manager: EntityStoreManager,
    ) -> None:
        super().__init__()
        self._dag = dag
        self._schemas = schemas
        self._evaluation_result_store_manager = EvaluationResultStoreManager(
            entity_store_manager
        )
        self._schema_online_schema_dag_mapper = (
            self.__init_schema_online_schema_dag_mapper(
                self._schemas, self._dag, self._evaluation_result_store_manager
            )
        )
        self._dag_effect_online_schema_dag_mapper = (
            self.__init_dag_effect_online_schema_dag_mapper(
                self._dag, self._evaluation_result_store_manager
            )
        )

    def evaluate(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[Vector]:
        if (
            online_schema_dag := self._schema_online_schema_dag_mapper.get(
                parsed_schema.schema
            )
        ) is not None:
            return online_schema_dag.evaluate(parsed_schema, context)
        raise InvalidSchemaException(
            f"Schema ({parsed_schema.schema._schema_name}) isn't present in the index."
        )

    def evaluate_by_dag_effect(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
        dag_effect: DagEffect,
    ) -> EvaluationResult[Vector]:
        if (
            online_schema_dag := self._dag_effect_online_schema_dag_mapper.get(
                dag_effect
            )
        ) is not None:
            return online_schema_dag.evaluate(parsed_schema, context)
        raise InvalidDagEffectException(
            f"DagEffect ({dag_effect}) isn't present in the index."
        )

    def __init_schema_online_schema_dag_mapper(
        self,
        schemas: set[SchemaObject],
        dag: Dag,
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> dict[SchemaObject, OnlineSchemaDag]:
        return {
            schema: OnlineSchemaDagCompiler(set(dag.nodes)).compile_schema_dag(
                dag.project_to_schema(schema),
                evaluation_result_store_manager,
            )
            for schema in schemas
        }

    def __init_dag_effect_online_schema_dag_mapper(
        self, dag: Dag, evaluation_result_store_manager: EvaluationResultStoreManager
    ) -> dict[DagEffect, OnlineSchemaDag]:
        dag_effect_schema_dag_map = {
            dag_effect: dag.project_to_dag_effect(dag_effect)
            for dag_effect in dag.dag_effects
        }
        return {
            dag_effect: OnlineSchemaDagCompiler(
                set(schema_dag.nodes)
            ).compile_schema_dag(
                schema_dag,
                evaluation_result_store_manager,
            )
            for dag_effect, schema_dag in dag_effect_schema_dag_map.items()
        }
