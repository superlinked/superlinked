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
from beartype.typing import Iterator, Mapping, Sequence, cast

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.event_aggregation_node import EventAggregationNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_dag import SchemaDag
from superlinked.framework.common.data_types import NodeDataTypes, Vector
from superlinked.framework.common.exception import InvalidStateException
from superlinked.framework.common.parser.parsed_schema import (
    ParsedSchema,
    ParsedSchemaWithEvent,
)
from superlinked.framework.common.schema.event_schema_object import SchemaReference
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage.entity.entity_id import EntityId
from superlinked.framework.common.storage_manager.entity_data_request import (
    EntityDataRequest,
    NodeDataRequest,
    NodeResultRequest,
)
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.telemetry.telemetry_registry import (
    TelemetryAttributeType,
    telemetry,
)
from superlinked.framework.compiler.online.online_schema_dag_compiler import (
    OnlineSchemaDagCompiler,
)
from superlinked.framework.online.dag.evaluation_result import EvaluationResult
from superlinked.framework.online.dag.online_schema_dag import OnlineSchemaDag
from superlinked.framework.online.dag_effect_group import DagEffectGroup
from superlinked.framework.online.online_entity_cache import OnlineEntityCache

logger = structlog.get_logger()


class OnlineDagEvaluator:
    def __init__(
        self,
        dag: Dag,
        schemas: set[IdSchemaObject],
        storage_manager: StorageManager,
    ) -> None:
        super().__init__()
        self._dag = dag
        self._schemas = schemas
        self._storage_manager = storage_manager
        self._schema_online_schema_dag_mapper = self.__init_schema_online_schema_dag_mapper(self._schemas, self._dag)
        self._dag_effect_group_to_online_schema_dag = self.__map_dag_effect_group_to_online_schema_dag(self._dag)
        self.__effect_to_group = self.__map_effect_to_group(self._dag_effect_group_to_online_schema_dag)
        self._log_dag_init()

    @property
    def effect_to_group(self) -> Mapping[DagEffect, DagEffectGroup]:
        return self.__effect_to_group

    def _log_dag_init(self) -> None:
        for schema, online_schema_dag in self._schema_online_schema_dag_mapper.items():
            logger.info(
                "initialized entity dag",
                schema=schema._schema_name,
                node_info=[(node.class_name, node.node_id) for node in online_schema_dag.nodes],
            )
        for dag_effect_group, online_schema_dag in self._dag_effect_group_to_online_schema_dag.items():
            logger.info(
                "initialized event dag",
                affected_schema=dag_effect_group.affected_schema._schema_name,
                affecting_schema=dag_effect_group.affecting_schema._schema_name,
                node_info=[(node.class_name, node.node_id) for node in online_schema_dag.nodes],
            )

    def __get_single_schema(self, parsed_schemas: Sequence[ParsedSchema]) -> IdSchemaObject:
        unique_schemas: set[IdSchemaObject] = {parsed_schema.schema for parsed_schema in parsed_schemas}
        if len(unique_schemas) != 1:
            raise InvalidStateException(
                "Multiple schemas are present among the parsed schemas.",
                schemas=[s._schema_name for s in unique_schemas],
            )
        return next(iter(unique_schemas))

    async def evaluate(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[Vector] | None]:
        index_schema = self.__get_single_schema(parsed_schemas)
        online_schema_dag = self._schema_online_schema_dag_mapper[index_schema]
        with telemetry.span(
            "dag.evaluate",
            attributes={"schema": index_schema._schema_name, "n_entities": len(parsed_schemas), "is_event": False},
        ):
            results = await online_schema_dag.evaluate(parsed_schemas, context, online_entity_cache)
        self.__log_evaluate(parsed_schemas, index_schema, results)
        return results

    async def evaluate_by_dag_effect_group(
        self,
        effect_group_to_parsed_schemas: Mapping[DagEffectGroup, list[ParsedSchemaWithEvent]],
        context: ExecutionContext,
        online_entity_cache: OnlineEntityCache,
    ) -> list[EvaluationResult[Vector] | None]:
        entity_data_requests = self._build_event_entity_data_requests(effect_group_to_parsed_schemas)
        await self._query_entity_data_requests(entity_data_requests, online_entity_cache)
        all_results = []
        for dag_effect_group, parsed_schema_with_events in effect_group_to_parsed_schemas.items():
            online_schema_dag = self._dag_effect_group_to_online_schema_dag[dag_effect_group]
            labels: dict[str, TelemetryAttributeType] = {
                "schema": dag_effect_group.affected_schema._schema_name,
                "n_entities": len(parsed_schema_with_events),
                "is_event": True,
            }
            with telemetry.span("dag.evaluate", attributes=labels):
                results = await online_schema_dag.evaluate(parsed_schema_with_events, context, online_entity_cache)
            logger.info("evaluated events", n_records=len(results))
            all_results.extend(results)
        return all_results

    def _build_event_entity_data_requests(
        self, effect_group_to_parsed_schemas: Mapping[DagEffectGroup, list[ParsedSchemaWithEvent]]
    ) -> list[EntityDataRequest]:
        requests = [
            request
            for dag_effect_group, parsed_schemas_with_event in effect_group_to_parsed_schemas.items()
            for node in self._dag_effect_group_to_online_schema_dag[dag_effect_group].persistable_nodes
            for referenced_schema, object_id in self._extract_schema_reference_fields(
                parsed_schemas_with_event, dag_effect_group
            )
            for request in self._create_entity_requests_for_effect_group(
                node, referenced_schema, object_id, dag_effect_group
            )
        ]
        return EntityDataRequest.merge(requests)

    def _extract_schema_reference_fields(
        self, parsed_schema_with_events: Sequence[ParsedSchemaWithEvent], dag_effect_group: DagEffectGroup
    ) -> Iterator[tuple[IdSchemaObject | None, str]]:
        for parsed_schema_with_event in parsed_schema_with_events:
            for field in parsed_schema_with_event.event_parsed_schema.fields:
                if isinstance(field.schema_field, SchemaReference):
                    yield self._get_referenced_schema(
                        field.schema_field._referenced_schema, dag_effect_group
                    ), field.value

    def _create_entity_requests_for_effect_group(
        self,
        node: Node,
        referenced_schema: IdSchemaObject | None,
        object_id: str,
        dag_effect_group: DagEffectGroup,
    ) -> Iterator[EntityDataRequest]:
        if referenced_schema:
            yield EntityDataRequest(
                EntityId(referenced_schema._schema_name, object_id),
                [NodeResultRequest(node.node_id, cast(type[NodeDataTypes], node.node_data_type))],
            )
        if isinstance(node, EventAggregationNode):
            yield EntityDataRequest(
                EntityId(dag_effect_group.affected_schema._schema_name, object_id),
                [
                    NodeDataRequest(node.node_id, metadata_id, int)
                    for metadata_id in [
                        constants.EFFECT_COUNT_KEY,
                        constants.EFFECT_AVG_TS_KEY,
                        constants.EFFECT_OLDEST_TS_KEY,
                    ]
                ],
            )

    def _get_referenced_schema(
        self, referenced_schema_type: type[IdSchemaObject], dag_effect_group: DagEffectGroup
    ) -> IdSchemaObject | None:
        schema_candidates = [dag_effect_group.affected_schema, dag_effect_group.affecting_schema]
        return next(iter(schema for schema in schema_candidates if isinstance(schema, referenced_schema_type)), None)

    async def _query_entity_data_requests(
        self, entity_data_requests: Sequence[EntityDataRequest], online_entity_cache: OnlineEntityCache
    ) -> None:
        stored_results = await self._storage_manager.read_entity_data_requests(entity_data_requests)
        online_entity_cache.load_node_info_into_cache(
            {
                entity_data_request.entity_id: node_result
                for entity_data_request, node_result in zip(entity_data_requests, stored_results)
            }
        )

    def __init_schema_online_schema_dag_mapper(
        self,
        schemas: set[IdSchemaObject],
        dag: Dag,
    ) -> dict[IdSchemaObject, OnlineSchemaDag]:
        return {
            schema: OnlineSchemaDagCompiler(set(dag.nodes)).compile_schema_dag(dag.project_to_schema(schema))
            for schema in schemas
        }

    def __map_dag_effect_group_to_online_schema_dag(self, dag: Dag) -> dict[DagEffectGroup, OnlineSchemaDag]:
        return {
            dag_effect_group: self.__compile_online_schema_dag(dag, dag_effect_group)
            for dag_effect_group in DagEffectGroup.group_similar_effects(dag.dag_effects)
        }

    def __compile_online_schema_dag(self, dag: Dag, dag_effect_group: DagEffectGroup) -> OnlineSchemaDag:
        nodes = self.__get_nodes_for_effect_group(dag, dag_effect_group)
        schema_dag = SchemaDag(dag_effect_group.event_schema, list(nodes))
        return OnlineSchemaDagCompiler(nodes).compile_schema_dag(schema_dag)

    def __get_nodes_for_effect_group(self, dag: Dag, dag_effect_group: DagEffectGroup) -> set[Node]:
        return {node for effect in dag_effect_group.effects for node in self.__get_nodes_for_effect(dag, effect)}

    def __get_nodes_for_effect(self, dag: Dag, dag_effect: DagEffect) -> set[Node]:
        nodes_to_visit: list[Node] = [dag.index_node]
        visited_nodes: set[Node] = set()
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            visited_nodes.add(current_node)
            parent_nodes = current_node.project_parents_for_dag_effect(dag_effect)
            nodes_to_visit.extend(node for node in parent_nodes if node not in visited_nodes)
        return visited_nodes

    def __map_effect_to_group(
        self, dag_effect_group_to_online_schema_dag: Mapping[DagEffectGroup, OnlineSchemaDag]
    ) -> dict[DagEffect, DagEffectGroup]:
        return {effect: group for group in dag_effect_group_to_online_schema_dag for effect in group.effects}

    def __log_evaluate(
        self,
        parsed_schemas: Sequence[ParsedSchema],
        index_schema: IdSchemaObject,
        results: Sequence[EvaluationResult[Vector] | None],
    ) -> None:
        logger_to_use = logger.bind(schema=index_schema._schema_name)
        logger_to_use.info("evaluated entities", n_entities=len(results))
        for i, result in enumerate(results):
            logger_to_use.debug(
                "evaluated entity",
                pii_vector=partial(str, result.main.value) if result is not None else "None",
                pii_field_values=[field.value for field in parsed_schemas[i].fields],
            )
