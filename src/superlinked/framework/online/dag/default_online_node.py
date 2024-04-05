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
from collections import defaultdict
from itertools import zip_longest
from typing import Generic

from typing_extensions import override

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.node import NDT, NT
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.online.dag.evaluation_result import (
    EvaluationResult,
    SingleEvaluationResult,
)
from superlinked.framework.online.dag.online_node import OnlineNode


class DefaultOnlineNode(OnlineNode[NT, NDT], ABC, Generic[NT, NDT]):
    @override
    def evaluate_self(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> list[EvaluationResult[NDT]]:
        parent_results = self.__get_parent_results(parsed_schemas, context)
        chunked_parent_results = self.__filter_chunked_parent_results(
            context, parent_results
        )

        main_inputs: dict[OnlineNode, list[SingleEvaluationResult]] = {
            node: [result.main for result in results]
            for node, results in parent_results.items()
        }

        mains: list[SingleEvaluationResult] = self._get_single_evaluation_results(
            self._evaluate_single_with_fallback(parsed_schemas, context, main_inputs)
        )

        chunk_inputs: dict[str, list[dict[OnlineNode, SingleEvaluationResult]]] = (
            self.__get_chunk_calculation_input(parsed_schemas, chunked_parent_results)
        )
        chunks_by_schema_id: dict[str, list[SingleEvaluationResult]] = (
            self.__evaluate_chunks(parsed_schemas, context, chunk_inputs)
        )

        return [
            EvaluationResult(
                main,
                chunks_by_schema_id.get(parsed_schemas[i].id_) or [],
            )
            for i, main in enumerate(mains)
        ]

    def __get_chunk_calculation_input(
        self,
        parsed_schemas: list[ParsedSchema],
        chunked_parent_results: dict[OnlineNode, list[EvaluationResult]],
    ) -> dict[str, list[dict[OnlineNode, SingleEvaluationResult]]]:
        calculation_input = {
            parsed_schema.id_: [
                {
                    **{
                        other_node: other_results[index].main
                        for other_node, other_results in chunked_parent_results.items()
                        if other_node.node_id != node.node_id
                    },
                    node: chunk,
                }
                for node, results in chunked_parent_results.items()
                if results
                for chunk in results[index].chunks
            ]
            for index, parsed_schema in enumerate(parsed_schemas)
        }

        return calculation_input

    def __evaluate_chunks(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
        chunk_calculation_input_by_schema_id: dict[
            str, list[dict[OnlineNode, SingleEvaluationResult]]
        ],
    ) -> dict[str, list[SingleEvaluationResult]]:
        chunked_results_by_schema_id: dict[str, list[SingleEvaluationResult]] = (
            defaultdict(list)
        )

        for chunk_dicts in zip_longest(
            *chunk_calculation_input_by_schema_id.values(), fillvalue={}
        ):
            nodes = set(
                node for chunk_dict in chunk_dicts for node in chunk_dict.keys()
            )
            # Merge results for the same node across different chunk_dicts
            merged_dict = {
                node: [
                    single_chunk_dict[node]
                    for single_chunk_dict in chunk_dicts
                    if node in single_chunk_dict
                ]
                for node in nodes
            }
            parsed_schemas_present: list[str] = [
                parsed_schemas[i].id_
                for i, single_chunk_dict in enumerate(chunk_dicts)
                if single_chunk_dict
            ]

            merged_result = self._get_single_evaluation_results(
                self._evaluate_single_with_fallback(
                    parsed_schemas, context, merged_dict
                )
            )

            for schema_id, result in zip(parsed_schemas_present, merged_result):
                chunked_results_by_schema_id[schema_id].append(result)

        return chunked_results_by_schema_id

    def _get_single_evaluation_results(
        self, values: list[NDT]
    ) -> list[SingleEvaluationResult[NDT]]:
        return [self._get_single_evaluation_result(value) for value in values]

    def __get_parent_results(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
    ) -> dict[OnlineNode, list[EvaluationResult]]:
        return {
            parent: parent.evaluate_next(parsed_schemas, context)
            for parent in self.parents
        }

    def __filter_chunked_parent_results(
        self,
        context: ExecutionContext,
        parent_results: dict[OnlineNode, list[EvaluationResult]],
    ) -> dict[OnlineNode, list[EvaluationResult]]:
        if context.is_query_context():
            return {}
        return {
            parent: results
            for parent, results in parent_results.items()
            if any(len(result.chunks) > 0 for result in results)
        }

    def _evaluate_single_with_fallback(
        self,
        parsed_schemas: list[ParsedSchema],
        context: ExecutionContext,
        parent_results: dict[OnlineNode, list[SingleEvaluationResult]],
    ) -> list[NDT]:
        single_result_all = self._evaluate_singles(parent_results, context)
        if single_result_all is not None:
            return single_result_all
        return self.get_fallback_result(parsed_schemas)

    @abstractmethod
    def _evaluate_singles(
        self,
        parent_results: dict[OnlineNode, list[SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> list[NDT] | None:
        pass

    def get_fallback_result(
        self,
        parsed_schemas: list[ParsedSchema],
    ) -> list[NDT]:
        stored_results = []
        for parsed_schema in parsed_schemas:
            stored_result = self.load_stored_result_or_raise_exception(parsed_schema)
            stored_results.append(stored_result)
        return stored_results
