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

from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, TypeVar

from typing_extensions import Self

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NDT, NT
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)

ONT = TypeVar("ONT", bound="OnlineNode")


class OnlineNode(ABC, Generic[NT, NDT], metaclass=ABCMeta):
    def __init__(
        self,
        node: NT,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        self.node = node
        self.children: list[OnlineNode] = []
        self.parents = parents
        self.evaluation_result_store_manager = evaluation_result_store_manager
        for parent in self.parents:
            parent.children.append(self)

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def node_id(self) -> str:
        return self.node.node_id

    def _get_single_evaluation_result(self, value: NDT) -> SingleEvaluationResult[NDT]:
        return SingleEvaluationResult(self.node_id, value)

    @classmethod
    @abstractmethod
    def from_node(
        cls,
        node: NT,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> Self:
        pass

    @classmethod
    @abstractmethod
    def get_node_type(cls) -> type[NT]:
        pass

    def evaluate_next(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[NDT]:
        result = self.evaluate_self(parsed_schema, context)
        if self.node.persist_evaluation_result:
            self.persist(result, parsed_schema, context)
        return result

    @abstractmethod
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[NDT]:
        pass

    def persist(
        self,
        result: EvaluationResult[NDT],
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> None:
        if context.is_query_context():
            return
        self.evaluation_result_store_manager.save_result(
            result,
            parsed_schema.id_,
            parsed_schema.schema._schema_name,
            self.node.persistence_type,
        )

    def load_stored_result(
        self, main_object_id: str, schema: SchemaObject
    ) -> NDT | None:
        stored_value: SingleEvaluationResult | None = (
            self.evaluation_result_store_manager.load_single_result(
                main_object_id,
                self.node_id,
                schema._schema_name,
                self.node.persistence_type,
            )
        )
        if stored_value:
            return stored_value.value
        return None
