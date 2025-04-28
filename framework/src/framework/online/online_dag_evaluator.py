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


from functools import partial

import structlog
from beartype.typing import Sequence

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InvalidDagEffectException,
    InvalidSchemaException,
)
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.compiler.online.online_schema_dag_compiler import (
    OnlineSchemaDagCompiler,
)
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_schema_dag import OnlineSchemaDag

logger = structlog.get_logger()


class OnlineDagEvaluator:
    def __init__(
        self,
        dag: Dag,
        schemas: set[SchemaObject],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__()
        self._dag = dag
        self._schemas = schemas
        self._schema_online_schema_dag_mapper = self.__init_schema_online_schema_dag_mapper(
            self._schemas, self._dag, storage_manager
        )
        self._dag_effect_online_schema_dag_mapper = self.__init_dag_effect_online_schema_dag_mapper(
            self._dag, storage_manager
        )
        self._log_dag_init()

    def _log_dag_init(self) -> None:
        for schema, online_schema_dag in self._schema_online_schema_dag_mapper.items():
            logger.info(
                "initialized entity dag",
                schema=schema._schema_name,
                node_info=[(node.class_name, node.node_id) for node in online_schema_dag.nodes],
            )
        for (
            dag_effect,
            online_schema_dag,
        ) in self._dag_effect_online_schema_dag_mapper.items():
            logger.info(
                "initialized event dag",
                affected_schema=dag_effect.resolved_affected_schema_reference.schema._schema_name,
                affecting_schema=dag_effect.resolved_affecting_schema_reference.schema._schema_name,
                node_info=[(node.class_name, node.node_id) for node in online_schema_dag.nodes],
            )

    def __get_single_schema(self, parsed_schemas: Sequence[ParsedSchema]) -> IdSchemaObject:
        unique_schemas: set[IdSchemaObject] = {parsed_schema.schema for parsed_schema in parsed_schemas}
        if len(unique_schemas) != 1:
            raise InvalidSchemaException(
                f"Multiple schemas ({[s._schema_name for s in unique_schemas]}) present in the index."
            )
        return next(iter(unique_schemas))

    def evaluate(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[Vector] | None]:
        index_schema = self.__get_single_schema(parsed_schemas)
        if (online_schema_dag := self._schema_online_schema_dag_mapper.get(index_schema)) is not None:
            results = online_schema_dag.evaluate(parsed_schemas, context)
            logger_to_use = logger.bind(schema=index_schema._schema_name)
            logger_to_use.info("evaluated entities", n_entities=len(results))
            for i, result in enumerate(results):
                logger_to_use.debug(
                    "evaluated entity",
                    pii_vector=partial(str, result.main.value) if result is not None else "None",
                    pii_field_values=[field.value for field in parsed_schemas[i].fields],
                )
            return results

        raise InvalidSchemaException(f"Schema ({index_schema._schema_name}) isn't present in the index.")

    def evaluate_by_dag_effect(
        self,
        parsed_schema_with_events: Sequence[ParsedSchemaWithEvent],
        context: ExecutionContext,
        dag_effect: DagEffect,
    ) -> list[EvaluationResult[Vector] | None]:
        if (online_schema_dag := self._dag_effect_online_schema_dag_mapper.get(dag_effect)) is not None:
            results = online_schema_dag.evaluate(parsed_schema_with_events, context)
            logger.info("evaluated events", n_records=len(results))
            return results
        raise InvalidDagEffectException(f"DagEffect ({dag_effect}) isn't present in the index.")

    def __init_schema_online_schema_dag_mapper(
        self,
        schemas: set[SchemaObject],
        dag: Dag,
        storage_manager: StorageManager,
    ) -> dict[SchemaObject, OnlineSchemaDag]:
        return {
            schema: OnlineSchemaDagCompiler(set(dag.nodes)).compile_schema_dag(
                dag.project_to_schema(schema),
                storage_manager,
            )
            for schema in schemas
        }

    def __init_dag_effect_online_schema_dag_mapper(
        self, dag: Dag, storage_manager: StorageManager
    ) -> dict[DagEffect, OnlineSchemaDag]:
        dag_effect_schema_dag_map = {
            dag_effect: dag.project_to_dag_effect(dag_effect) for dag_effect in dag.dag_effects
        }
        return {
            dag_effect: OnlineSchemaDagCompiler(set(schema_dag.nodes)).compile_schema_dag(
                schema_dag,
                storage_manager,
            )
            for dag_effect, schema_dag in dag_effect_schema_dag_map.items()
        }
