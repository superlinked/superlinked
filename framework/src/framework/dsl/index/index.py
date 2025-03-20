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

import datetime

import structlog
from beartype.typing import Sequence, cast
from typing_extensions import Annotated

from superlinked.framework.common.const import constants
from superlinked.framework.common.dag.concatenation_node import ConcatenationNode
from superlinked.framework.common.dag.dag import Dag
from superlinked.framework.common.dag.dag_effect import DagEffect
from superlinked.framework.common.dag.effect_modifier import EffectModifier
from superlinked.framework.common.dag.index_node import IndexNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    InitializationException,
    RecursionException,
    ValidationException,
)
from superlinked.framework.common.schema.event_schema_object import EventSchemaObject
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField, SchemaObject
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.effect import Effect
from superlinked.framework.dsl.index.util.aggregation_effect_group import (
    AggregationEffectGroup,
)
from superlinked.framework.dsl.index.util.aggregation_node_util import (
    AggregationNodeUtil,
)
from superlinked.framework.dsl.index.util.effect_with_referenced_schema_object import (
    EffectWithReferencedSchemaObject,
)
from superlinked.framework.dsl.space.space import Space

logger = structlog.getLogger()

ValidatedSpaceList = Annotated[list[Space], TypeValidator.list_validator(Space)]
ValidatedSchemaFieldList = Annotated[list[SchemaField | None], TypeValidator.list_validator(SchemaField)]
ValidatedEffectList = Annotated[list[Effect], TypeValidator.list_validator(Effect)]


class Index:  # pylint: disable=too-many-instance-attributes
    """
    An index is an abstraction which represents a collection of spaces that will enable us to query our data.
    """

    @TypeValidator.wrap
    def __init__(  # pylint: disable=too-many-arguments
        self,
        spaces: Space | ValidatedSpaceList,
        fields: SchemaField | ValidatedSchemaFieldList | None = None,
        effects: Effect | ValidatedEffectList | None = None,
        max_age: datetime.timedelta | None = None,
        max_count: int | None = None,
        temperature: int | float = 0.5,
        event_influence: int | float = 0.5,
        time_decay_floor: int | float = 1.0,
    ) -> None:
        """
        Initialize the Index.

        Args:
            spaces (Space | list[Space]): The space or list of spaces.
            fields (SchemaField | list[SchemaField]): The field or list of fields to be indexed.
            effects (Effect | list[Effect]): A list of conditional interactions within a `Space`.
                Defaults to None.
            max_age (datetime.timedelta | None): Maximum age of events to be considered. Older events
                will be filtered out, if specified. Defaults to None meaning no restriction.
            max_count (int | None): Only affects the batch system! Restricts how many events should be considered,
                based on their age. Defaults to None meaning no restriction.
            temperature (float): Controls how much each event contributes when aggregating events together.
                Must be between 0 and 1. Values closer to 0 give more weight to the stored event aggregate,
                while values closer to 1 give more weight to the new event being added. Defaults to 0.5 for
                balanced weighting.
            event_influence (float): Controls how much the final aggregated event vector influences the base vector.
                Must be between 0 and 1. Values closer to 0 keep the result closer to the base vector, while values
                closer to 1 make the result more influenced by the aggregated events.
                Defaults to 0.5 for balanced influence.
            time_decay_floor (float): Controls the time decay curve for event weights.
                Higher values create a more gradual decay, while lower values create steeper decay.
                Defaults to 1.0.

        Raises:
            InitializationException: If no spaces are provided.
        """
        event_modifier = EffectModifier(max_age, max_count, temperature, event_influence, time_decay_floor)
        self.__spaces = self.__init_spaces(spaces)
        self.__space_schemas = self.__init_node_schemas(self.__spaces)
        self.__fields = self.__init_fields(fields)
        effects_with_schema = self.__init_effects_with_schema(effects, self.__spaces)
        self.__effect_schemas = self.__init_effect_schemas(effects_with_schema)
        self.__schemas = list(set(self.__space_schemas).union(set(self.__effect_schemas)))
        self.__node = self.__init_index_node(self.__spaces, effects_with_schema, event_modifier)
        self.__dag_effects = self.__init_dag_effects(effects_with_schema)
        self.__dag = self.__init_dag(self.__node, self.__dag_effects)
        self.__schema_type_schema_mapper = self.__init_schema_type_schema_mapper(effects_with_schema)
        self._logger = logger.bind(
            node_id=self._node_id,
            space_ids=[hash(space) for space in self._spaces],
            space_types=[space.__class__.__name__ for space in self._spaces],
            field_ids=[hash(field) for field in self._fields],
            field_types=[field.__class__.__name__ for field in self._fields],
        )
        self._logger.info("initialized index")

    @property
    def schemas(self) -> Sequence[SchemaObject]:
        return self.__schemas

    @property
    def _spaces(self) -> Sequence[Space]:
        return self.__spaces

    @property
    def _space_schemas(self) -> list[SchemaObject]:
        return self.__space_schemas

    @property
    def _effect_schemas(self) -> list[EventSchemaObject]:
        return self.__effect_schemas

    @property
    def _node(self) -> IndexNode:
        return self.__node

    @property
    def _fields(self) -> Sequence[SchemaField]:
        return self.__fields

    @property
    def non_nullable_fields(self) -> Sequence[SchemaField]:
        return [field for field in self.__fields if not field.nullable]

    @property
    def _node_id(self) -> str:
        return self.__node.node_id

    @property
    def _dag_effects(self) -> set[DagEffect]:
        return self.__dag_effects

    @property
    def _dag(self) -> Dag:
        return self.__dag

    @property
    def _schema_type_schema_mapper(self) -> dict[type[SchemaObject], IdSchemaObject]:
        return self.__schema_type_schema_mapper

    def has_space(self, space: Space) -> bool:
        """
        Check, if the given space is present in the index.

        Args:
            space (Space): The space to check.

        Returns:
            bool: True if the index has the space, False otherwise.
        """
        return space in self.__spaces

    def has_schema(self, schema: SchemaObject) -> bool:
        """
        Check, if the given schema is listed as an input to any of the spaces of the index.

        Args:
            schema (SchemaObject): The schema to check.

        Returns:
            bool: True if the index has the schema, False otherwise.
        """
        return schema in self.__schemas

    def __init_spaces(self, spaces: Space | list[Space]) -> list[Space]:
        if not isinstance(spaces, Sequence):
            spaces = [spaces]
        if len(spaces) == 0:
            raise InitializationException("Index must be built on at least 1 space.")
        if len(set(spaces)) != len(spaces):
            raise InitializationException("Index cannot contain duplicate spaces.")
        return spaces

    def __init_node_schemas(self, validated_spaces: list[Space]) -> list[SchemaObject]:
        seen = set[SchemaObject]()
        seen_add = seen.add
        return [
            schema
            for space in validated_spaces
            for node in space._get_all_embedding_nodes()
            for schema in node.schemas
            if not (schema in seen or seen_add(schema))
        ]

    def __init_fields(self, fields: SchemaField | Sequence[SchemaField | None] | None) -> Sequence[SchemaField]:
        if fields is None:
            return []
        if not isinstance(fields, Sequence):
            return [fields]
        if None in fields:
            raise ValidationException("Fields cannot contain None values")
        return cast(Sequence[SchemaField], fields)

    def __init_effects_with_schema(
        self, effects: Effect | list[Effect] | None, spaces: list[Space]
    ) -> list[EffectWithReferencedSchemaObject]:
        if effects is None:
            effects = []
        if not isinstance(effects, Sequence):
            effects = [effects]
        self.__validate_effects(effects, spaces)
        return [
            EffectWithReferencedSchemaObject.from_base_effect(effect, set(self.__space_schemas)) for effect in effects
        ]

    def __init_effect_schemas(self, effects: list[EffectWithReferencedSchemaObject]) -> list[EventSchemaObject]:
        seen = set[EventSchemaObject]()
        seen_add = seen.add
        return [
            effect_with_schema.event_schema
            for effect_with_schema in effects
            if not (effect_with_schema.event_schema in seen or seen_add(effect_with_schema.event_schema))
        ]

    def __validate_effects(self, effects: list[Effect], spaces: list[Space]) -> None:
        invalid_space_effects = [effect for effect in effects if effect.space not in spaces]
        if invalid_space_effects:
            raise ValidationException(f"Effects must work on the Index's spaces, got ({invalid_space_effects})")

    def __init_index_node(
        self,
        spaces: list[Space],
        effects: list[EffectWithReferencedSchemaObject],
        effect_modifier: EffectModifier,
    ) -> IndexNode:
        index_parents = set[Node[Vector]]()
        for schema in self.__space_schemas:
            parents = [
                self.__init_parent_for_index_or_aggregation(space, schema, effects, effect_modifier) for space in spaces
            ]
            if len(spaces) == 1:
                index_parents.update(parents)
            else:
                index_parents.add(ConcatenationNode(parents))
        return IndexNode(index_parents)

    def __init_dag_effects(self, effects_with_schema: list[EffectWithReferencedSchemaObject]) -> set[DagEffect]:
        return {effect.dag_effect for effect in effects_with_schema}

    def __init_parent_for_index_or_aggregation(
        self,
        space: Space[AggregationInputT, EmbeddingInputT],
        schema: SchemaObject,
        effects: Sequence[EffectWithReferencedSchemaObject],
        effect_modifier: EffectModifier,
    ) -> Node[Vector]:
        filtered_effects = Index.__filter_effects_by_space_and_schema(
            effects=effects,
            space=space,
            schema=schema,
        )
        if not filtered_effects:
            return space._get_embedding_node(schema)
        aggregation_effect_group = AggregationEffectGroup.from_filtered_effects(filtered_effects)
        return AggregationNodeUtil.init_aggregation_node(aggregation_effect_group, effect_modifier)

    @staticmethod
    def __filter_effects_by_space_and_schema(
        effects: Sequence[EffectWithReferencedSchemaObject],
        space: Space[AggregationInputT, EmbeddingInputT],
        schema: SchemaObject,
    ) -> list[EffectWithReferencedSchemaObject[AggregationInputT, EmbeddingInputT]]:
        return [
            effect
            for effect in effects
            if effect.base_effect.space == space and effect.resolved_affected_schema_reference.schema == schema
        ]

    def __init_dag(self, node: IndexNode, dag_effects: set[DagEffect]) -> Dag:
        def append_ancestors(node: Node, depth: int = 0) -> None:
            if depth > constants.MAX_DAG_DEPTH:
                raise RecursionException(f"Max DAG depth ({constants.MAX_DAG_DEPTH}) exceeded.")
            dag_dict[node.node_id] = node
            for parent in node.parents:
                append_ancestors(parent, depth + 1)

        dag_dict: dict[str, Node] = {}
        append_ancestors(node)
        return Dag(
            list(dag_dict.values()),
            dag_effects,
        )

    def __init_schema_type_schema_mapper(
        self, effects: list[EffectWithReferencedSchemaObject]
    ) -> dict[type[SchemaObject], IdSchemaObject]:
        resolved_schema_references = {
            effect_with_schema.resolved_affected_schema_reference for effect_with_schema in effects
        }.union({effect_with_schema.resolved_affecting_schema_reference for effect_with_schema in effects})
        return {
            resolved_schema_reference.reference_field._referenced_schema: resolved_schema_reference.schema
            for resolved_schema_reference in resolved_schema_references
        }
