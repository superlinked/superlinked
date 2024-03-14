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
from typing import Generic

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NDT, NT
from superlinked.framework.common.exception import DagEvaluationException
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.dag.online_node import OnlineNode


class DefaultOnlineNode(OnlineNode[NT, NDT], ABC, Generic[NT, NDT]):
    def evaluate_self(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> EvaluationResult[NDT]:
        parent_results = self.__get_parent_results(parsed_schema, context)
        chunked_parent_results = self.__filter_chunked_parent_results(
            context, parent_results
        )
        main_inputs = {parent: result.main for parent, result in parent_results.items()}
        input_parent_results: list[dict[OnlineNode, SingleEvaluationResult]] = [
            self.__get_chunked_input(parent_results, chunked_parent, chunked_result)
            for chunked_parent, chunked_results in chunked_parent_results.items()
            for chunked_result in chunked_results.chunks
        ]
        main: SingleEvaluationResult = self._get_single_evaluation_result(
            self._evaluate_single_with_fallback(parsed_schema, context, main_inputs)
        )
        chunks: list[SingleEvaluationResult] = [
            self._get_single_evaluation_result(
                self._evaluate_single_with_fallback(parsed_schema, context, input_)
            )
            for input_ in input_parent_results
        ]
        return EvaluationResult(
            main,
            chunks,
        )

    def __get_parent_results(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
    ) -> dict[OnlineNode, EvaluationResult]:
        return {
            parent: parent.evaluate_next(parsed_schema, context)
            for parent in self.parents
        }

    def __filter_chunked_parent_results(
        self,
        context: ExecutionContext,
        parent_results: dict[OnlineNode, EvaluationResult],
    ) -> dict[OnlineNode, EvaluationResult]:
        return (
            {}
            if context.is_query_context()
            else {
                parent: result
                for parent, result in parent_results.items()
                if len(result.chunks) > 0
            }
        )

    def __get_chunked_input(
        self,
        parent_results: dict[OnlineNode, EvaluationResult],
        chunked_parent: OnlineNode,
        chunked_result: SingleEvaluationResult,
    ) -> dict[OnlineNode, SingleEvaluationResult]:
        input_parent_results = {
            parent: result.main
            for parent, result in parent_results.items()
            if parent.node_id != chunked_parent.node_id
        }
        input_parent_results[chunked_parent] = chunked_result
        return input_parent_results

    def _evaluate_single_with_fallback(
        self,
        parsed_schema: ParsedSchema,
        context: ExecutionContext,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
    ) -> NDT:
        single_result = self._evaluate_single(parent_results, context)
        if single_result is not None:
            return single_result
        return self.get_fallback_result(parsed_schema)

    @abstractmethod
    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> NDT | None:
        pass

    def get_fallback_result(
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
