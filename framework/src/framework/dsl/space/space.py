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

from abc import ABC, abstractmethod

from beartype.typing import Mapping, TypeAlias, TypeVar

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.schema.schema_object import SchemaField, SchemaObject
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.space.exception import InvalidSpaceParamException

# SpaceInputType
SIT = TypeVar("SIT", bound=SchemaField)


class Space(ABC):
    """
    Abstract base class for a space.

    This class defines the interface for a space in the context of the application.
    """

    def __init__(self, fields: SIT | list[SIT], type_: type | TypeAlias) -> None:
        super().__init__()
        field_list: list[SIT] = fields if isinstance(fields, list) else [fields]
        TypeValidator.validate_list_item_type(field_list, type_, "field_list")
        self.__validate_fields(field_list)
        self._field_set = set(field_list)

    def __validate_fields(self, field_list: list[SIT]) -> None:
        if not self._allow_empty_fields and not field_list:
            raise InvalidSpaceParamException(
                f"{self.__class__.__name__} field input must not be empty."
            )
        schema_list = [field.schema_obj for field in field_list]
        if duplicates := [
            schema._schema_name
            for schema in schema_list
            if schema_list.count(schema) > 1
        ]:
            raise InvalidSpaceParamException(
                f"Duplicates schemas in the same space are not allowed. Duplicates: {duplicates}"
            )

    @property
    @abstractmethod
    def annotation(self) -> str: ...

    @property
    @abstractmethod
    def _allow_empty_fields(self) -> bool: ...

    @property
    @abstractmethod
    def _node_by_schema(self) -> Mapping[SchemaObject, Node[Vector]]: ...

    def _get_node(self, schema: SchemaObject) -> Node[Vector]:
        if node := self._node_by_schema.get(schema):
            return node
        return self._handle_node_not_present(schema)

    def _handle_node_not_present(self, schema: SchemaObject) -> Node[Vector]:
        raise InvalidSchemaException(
            f"There's no node corresponding to this schema: {schema._schema_name}"
        )

    def _get_all_leaf_nodes(self) -> set[Node[Vector]]:
        return set(self._node_by_schema.values())
