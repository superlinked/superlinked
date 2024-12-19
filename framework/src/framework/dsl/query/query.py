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

from beartype.typing import Mapping

from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import NumericParamType
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor
from superlinked.framework.dsl.space.space import Space


@TypeValidator.wrap
class Query:
    """
    A class representing a query. Build queries using Params as placeholders for weights or query text,
    and supply their value later on when executing a query.

    Attributes:
        index (Index): The index to be used for the query.
        weights (Mapping[Space, NumericParamType] | None, optional): The mapping of spaces to weights.
            Defaults to None, which is equal weight for each space.
    """

    def __init__(self, index: Index, weights: Mapping[Space, NumericParamType] | None = None) -> None:
        """
        Initialize the Query.

        Args:
            index (Index): The index to be used for the query.
            weights (Mapping[Space, NumericParamType] | None, optional): The mapping of spaces to weights.
                Defaults to None, which is equal weight for each space.
        """
        self.index = index
        self.weight_by_space: Mapping[Space, NumericParamType] = weights or {}

    def find(self, schema: IdSchemaObject) -> QueryDescriptor:
        """
        Find a schema in the query.

        Args:
            schema (IdSchemaObject): The schema to find.

        Returns:
            QueryDescriptor: The QueryDescriptor object.

        Raises:
            QueryException: If the index does not have the queried schema.
        """
        return QueryDescriptor(self.index, schema).space_weights(self.weight_by_space)
