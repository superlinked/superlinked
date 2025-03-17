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

from dataclasses import dataclass

from beartype.typing import Any, cast
from typing_extensions import override

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ITERABLE_COMPARISON_OPERATION_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.dsl.query.clause_params import KNNSearchClauseParams
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
    NLQAnnotationType,
)
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
)
from superlinked.framework.dsl.query.query_filter_validator import QueryFilterValidator


@dataclass(frozen=True)
class HardFilterClause(SingleValueParamQueryClause, NLQCompatible):
    op: ComparisonOperationType
    operand: SchemaField
    group_key: int | None

    @property
    @override
    def is_type_mandatory_in_nlq(self) -> bool:
        return False

    @property
    @override
    def nlq_annotations(self) -> list[NLQAnnotation]:
        value_param = QueryClause.get_param(self.value_param)
        value_accepted_type = GenericClassUtil.get_single_generic_type(self.operand)
        options = QueryClause._format_param_options(value_param)
        description = value_param.description or ""
        annotation = "".join(
            (
                f"  - {value_param.name}: A {value_accepted_type.__name__} "
                f"that must {self.op.value.replace('_', ' ')} the `{self.operand.name}` field.",
                f"\n    - **Possible values:** {options}." if options else "",
                f"\n    - **Description:** {description}" if description else "",
            )
        )
        return [NLQAnnotation(annotation, NLQAnnotationType.EXACT_VALUE_REQUIRED)]

    @override
    def get_altered_knn_search_params(self, knn_search_clause_params: KNNSearchClauseParams) -> KNNSearchClauseParams:
        hard_filter = self.__evaluate()
        if hard_filter is None:
            return knn_search_clause_params
        hard_filters = list(knn_search_clause_params.filters)
        hard_filters.append(hard_filter)
        return knn_search_clause_params.set_params(filters=hard_filters)

    @override
    def _get_default_value_param_name(self) -> str:
        return f"hard_filter_{self.operand.name}_{self.op.value}_param__"

    def __evaluate(self) -> ComparisonOperation[SchemaField] | None:
        value = self._get_value()
        if value is None:
            return None
        operation = ComparisonOperation(self.op, self.operand, value, self.group_key)
        QueryFilterValidator.validate_operation_operand_type(operation, allow_param=False)
        return operation

    @classmethod
    def from_param(cls, operation: ComparisonOperation[SchemaField]) -> HardFilterClause:
        schema_field = cast(SchemaField, operation._operand)
        param_type: Any = GenericClassUtil.get_single_generic_type(schema_field)
        if operation._op in ITERABLE_COMPARISON_OPERATION_TYPES:
            param_type = list[param_type]
        return HardFilterClause(
            QueryClause._to_typed_param(operation._other, [param_type]),
            operation._op,
            schema_field,
            operation._group_key,
        )
