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
from functools import partial

import structlog
from beartype.typing import Generic, TypeVar

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import NDT, NT
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.schema_object import SchemaObject
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.dag.parent_validator import ParentValidationType

ONT = TypeVar("ONT", bound="OnlineNode")

logger = structlog.get_logger()


class OnlineNode(ABC, Generic[NT, NDT], metaclass=ABCMeta):
    def __init__(
        self,
        node: NT,
        parents: list[OnlineNode],
        storage_manager: StorageManager,
        parent_validation_type: ParentValidationType = ParentValidationType.NO_VALIDATION,
    ) -> None:
        self.node = node
        self.children: list[OnlineNode] = []
        self.parents = parents
        self.storage_manager = storage_manager
        self.validate_parents(parent_validation_type)
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

    def evaluate_next(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[NDT]]:
        results = self.evaluate_self(parsed_schemas, context)
        if self.node.persist_evaluation_result and not context.is_query_context:
            for i, result in enumerate(results):
                self.persist(result, parsed_schemas[i])
        return results

    def evaluate_next_single(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[NDT]:
        return self.evaluate_next([parsed_schema], context)[0]

    @abstractmethod
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[NDT]]:
        pass

    def persist(
        self,
        result: EvaluationResult[NDT],
        parsed_schema: ParsedSchema,
    ) -> None:
        self.storage_manager.write_node_result(
            parsed_schema.schema,
            parsed_schema.id_,
            result.main.node_id,
            result.main.value,
        )
        for chunk in result.chunks:
            self.storage_manager.write_node_result(
                parsed_schema.schema,
                chunk.object_id,
                chunk.node_id,
                chunk.value,
                parsed_schema.id_,
            )
        logger.debug(
            "stored online node data",
            schema=parsed_schema.schema._schema_name,
            pii_main_result=partial(str, result.main.value),
            pii_chunk_result=lambda: [str(chunk.value) for chunk in result.chunks],
        )

    def load_stored_result(self, object_id: str, schema: SchemaObject) -> NDT | None:
        return self.storage_manager.read_node_result(
            schema,
            object_id,
            self.node_id,
            self.node.node_data_type,
        )

    def load_stored_result_or_raise_exception(
        self,
        parsed_schema: ParsedSchema,
    ) -> NDT:
        stored_result = self.load_stored_result(parsed_schema.id_, parsed_schema.schema)
        if stored_result is None:
            raise DagEvaluationException(
                f"{self.node_id} doesn't have a stored value for (schema, object_id):"
                + f" ({parsed_schema.schema._schema_name}, {parsed_schema.id_})"
            )
        return stored_result

    def validate_parents(
        self,
        parent_validation_type: ParentValidationType,
    ) -> None:
        if not parent_validation_type.validator(len(self.parents)):
            raise ParentCountException(
                f"{type(self).__name__} must have {parent_validation_type.description}."
            )
