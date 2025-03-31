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

import hashlib
from abc import abstractmethod

from beartype.typing import Generic, Sequence, TypeAlias, TypeVar
from typing_extensions import override

from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.embedding_node import EmbeddingNode
from superlinked.framework.common.data_types import NodeDataTypes
from superlinked.framework.common.schema.schema_object import (
    ConcreteSchemaField,
    DescribedBlob,
    Number,
    SchemaField,
    SchemaObject,
)
from superlinked.framework.common.space.config.aggregation.aggregation_config import (
    AggregationInputT,
)
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingInputT,
)
from superlinked.framework.common.space.interface.has_transformation_config import (
    HasTransformationConfig,
)
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.space.exception import InvalidSpaceParamException

# SpaceInputType
SIT = TypeVar("SIT", bound=NodeDataTypes)
PYTHON_MULTILINE_STRING_DELIMITER = "\n        "

SpaceFieldT = TypeVar(
    "SpaceFieldT",
    bound=ChunkingNode | ConcreteSchemaField | DescribedBlob | Number,
)


class Space(
    HasTransformationConfig[AggregationInputT, EmbeddingInputT],
    Generic[AggregationInputT, EmbeddingInputT],
):
    """
    Abstract base class for a space.

    This class defines the interface for a space in the context of the application.
    """

    def __init__(self, fields: Sequence[SchemaField], type_: type | TypeAlias) -> None:
        super().__init__()
        TypeValidator.validate_list_item_type(fields, type_, "field_list")
        self.__validate_fields(fields)
        self._field_set = set(fields)

    def __validate_fields(self, field_list: Sequence[SchemaField]) -> None:
        if not self._allow_empty_fields and not field_list:
            raise InvalidSpaceParamException(f"{self.__class__.__name__} field input must not be empty.")
        schema_list = [field.schema_obj for field in field_list]
        if duplicates := [schema._schema_name for schema in schema_list if schema_list.count(schema) > 1]:
            raise InvalidSpaceParamException(
                f"Duplicates schemas in the same space are not allowed. Duplicates: {duplicates}"
            )

    def _fields_to_non_none_sequence(
        self, fields: SpaceFieldT | None | Sequence[SpaceFieldT | None]
    ) -> list[SpaceFieldT]:
        fields = fields if isinstance(fields, Sequence) else [fields]
        return [field for field in fields if field]

    @property
    @override
    def length(self) -> int:
        return self.transformation_config.length

    @property
    def allow_similar_clause(self) -> bool:
        # To be overridden in child classes
        return True

    @property
    def annotation(self) -> str:
        return self._annotation.replace(PYTHON_MULTILINE_STRING_DELIMITER, " ")

    @property
    @abstractmethod
    def _annotation(self) -> str: ...

    @property
    @abstractmethod
    def _allow_empty_fields(self) -> bool: ...

    @abstractmethod
    def _create_default_node(self, schema: SchemaObject) -> EmbeddingNode[AggregationInputT, EmbeddingInputT]: ...

    @property
    @abstractmethod
    def _embedding_node_by_schema(
        self,
    ) -> dict[SchemaObject, EmbeddingNode[AggregationInputT, EmbeddingInputT]]: ...

    def _get_embedding_node(self, schema: SchemaObject) -> EmbeddingNode[AggregationInputT, EmbeddingInputT]:
        if node := self._embedding_node_by_schema.get(schema):
            return node
        return self._handle_embedding_node_not_present(schema)

    def _handle_embedding_node_not_present(
        self, schema: SchemaObject
    ) -> EmbeddingNode[AggregationInputT, EmbeddingInputT]:
        embedding_node = self._create_default_node(schema)
        self._embedding_node_by_schema[schema] = embedding_node
        return embedding_node

    def _get_all_embedding_nodes(
        self,
    ) -> set[EmbeddingNode[AggregationInputT, EmbeddingInputT]]:
        return set(self._embedding_node_by_schema.values())

    @override
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Space)
            and self.transformation_config == other.transformation_config
            and self._field_set == other._field_set
        )

    @override
    def __hash__(self) -> int:
        return hash((self.transformation_config, frozenset(self._field_set)))

    @override
    def __str__(self) -> str:
        space_hash = hashlib.md5(str(hash(self)).encode()).hexdigest()[:4]
        return f"{type(self).__name__}_{space_hash}"
