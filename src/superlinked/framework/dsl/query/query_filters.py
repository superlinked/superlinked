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

from itertools import groupby
from typing import cast

from superlinked.framework.common.exception import (
    NotImplementedException,
    QueryException,
)
from superlinked.framework.dsl.query.param_evaluator import ParamEvaluator
from superlinked.framework.dsl.query.predicate.binary_op import BinaryOp
from superlinked.framework.dsl.query.predicate.binary_predicate import BinaryPredicate
from superlinked.framework.dsl.query.predicate.evaluated_binary_predicate import (
    EvaluatedBinaryPredicate,
)
from superlinked.framework.dsl.query.predicate.query_predicate import QueryPredicate

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["QueryFilters"] = False

SUPPORTED_BINARY_OPS = {BinaryOp.SIMILAR, BinaryOp.LOOKS_LIKE}


class QueryFilters:
    def __init__(
        self, filters: list[QueryPredicate], param_evaluator: ParamEvaluator
    ) -> None:
        evaluated_filters = param_evaluator.evaluate_filters(
            self._validate_filters(filters)
        )
        self.grouped_evaluated_filters: dict[
            BinaryOp, list[EvaluatedBinaryPredicate]
        ] = self.__group_filters(evaluated_filters)
        self.__similar_filters = self.grouped_evaluated_filters.get(
            BinaryOp.SIMILAR, []
        )
        looks_like_filters = self.grouped_evaluated_filters.get(BinaryOp.LOOKS_LIKE, [])
        self.__looks_like_filter = looks_like_filters[0] if looks_like_filters else None
        self.__filter_count = len(evaluated_filters)

    @property
    def similar_filters(self) -> list[EvaluatedBinaryPredicate]:
        return self.__similar_filters

    @property
    def looks_like_filter(self) -> EvaluatedBinaryPredicate | None:
        return self.__looks_like_filter

    @property
    def filter_count(self) -> int:
        return self.__filter_count

    def _validate_filters(self, filters: list[QueryPredicate]) -> list[BinaryPredicate]:
        self._check_operations_are_supported(filters)
        self._check_filter_class_is_supported(filters)
        binary_filters = cast(list[BinaryPredicate], filters)
        self._check_similar_filters(binary_filters)
        self._check_looks_like_filters(binary_filters)
        return binary_filters

    def __group_filters(
        self, evaluated_binary_predicates: list[EvaluatedBinaryPredicate]
    ) -> dict[BinaryOp, list[EvaluatedBinaryPredicate]]:
        return cast(
            dict[BinaryOp, list[EvaluatedBinaryPredicate]],
            {
                operation_type: list(group_)
                for operation_type, group_ in groupby(
                    sorted(
                        evaluated_binary_predicates,
                        key=QueryFilters._get_operation_type_hash,
                    ),
                    QueryFilters._get_operation_type,
                )
            },
        )

    def _check_operations_are_supported(self, filters: list[QueryPredicate]) -> None:
        if unsupported_ops := ", ".join(
            [
                str(filter_.op)
                for filter_ in filters
                if filter_.op not in SUPPORTED_BINARY_OPS
            ]
        ):
            raise NotImplementedException(
                f"Unsupported filter op(s): {unsupported_ops}"
            )

    def _check_filter_class_is_supported(self, filters: list[QueryPredicate]) -> None:
        if any(
            filter_ for filter_ in filters if not isinstance(filter_, BinaryPredicate)
        ):
            unsupported_types = ", ".join(
                [
                    type(filter_).__name__
                    for filter_ in filters
                    if not isinstance(filter_, BinaryPredicate)
                ]
            )
            raise NotImplementedException(
                f"Unsupported filter type(s): {unsupported_types}"
            )

    def _check_similar_filters(self, filters: list[BinaryPredicate]) -> None:
        if invalid_nodes := [
            filter_
            for filter_ in filters
            if filter_.op == BinaryOp.SIMILAR and filter_.left_param_node is None
        ]:
            raise NotImplementedException(
                f"Unsupported similar filter: {invalid_nodes}"
            )

    def _check_looks_like_filters(self, filters: list[BinaryPredicate]) -> None:
        if (
            looks_like_filter_count := len(
                [filter_ for filter_ in filters if filter_.op == BinaryOp.LOOKS_LIKE]
            )
        ) > 1:
            raise QueryException(
                f"One query cannot have more than one looks like filter, got {looks_like_filter_count}"
            )

    @staticmethod
    def _get_operation_type(binary_predicate: EvaluatedBinaryPredicate) -> BinaryOp:
        return binary_predicate.predicate.op

    @staticmethod
    def _get_operation_type_hash(
        binary_predicate: EvaluatedBinaryPredicate,
    ) -> int:
        return hash(binary_predicate.predicate.op)
