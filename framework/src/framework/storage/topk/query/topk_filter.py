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

from dataclasses import dataclass

from beartype.typing import Any
from topk_sdk.query import field as topk_field
from topk_sdk.query import not_

from superlinked.framework.common.exception import (
    FeatureNotSupportedException,
    NotImplementedException,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.query.vdb_filter import VDBFilter
from superlinked.framework.storage.topk.query.topk_filter_information import (
    FilterCombinator,
    FilterOperator,
    TopKFilterInformation,
)
from superlinked.framework.storage.topk.topk_field_descriptor_compiler import (
    TopKFieldDescriptorCompiler,
)


@dataclass(frozen=True)
class TopKFilter(VDBFilter):
    def to_expression(self) -> Any:
        filter_info = TopKFilterInformation.get(self.op)
        values = filter_info.get_value_mapper_fn()(self.field_value)
        filter_expressions = [
            self._calculate_expression(self.field, filter_info.filter_operator, value) for value in values
        ]
        combined_expression = filter_info.get_combination_fn()(filter_expressions)
        return combined_expression

    @classmethod
    def _calculate_expression(cls, field: Field, filter_operator: FilterOperator, value: Any) -> Any:
        field_name = TopKFieldDescriptorCompiler._encode_field_name(field.name)

        match filter_operator:
            case FilterOperator.EQ:
                if isinstance(value, list):
                    expression = FilterCombinator.combine_with_or([topk_field(field_name).contains(v) for v in value])
                elif isinstance(value, (str, int, float, bool)):
                    expression = topk_field(field_name) == value
                else:
                    raise FeatureNotSupportedException(f"Unsupported value type for EQ: {type(value)}")
                return expression
            case FilterOperator.NE:
                if isinstance(value, list):
                    expression = FilterCombinator.combine_with_and(
                        [not_(topk_field(field_name).contains(v)) for v in value]
                    )
                elif isinstance(value, (str, int, float, bool)):
                    expression = topk_field(field_name) != value
                else:
                    raise FeatureNotSupportedException(f"Unsupported value type for NE: {type(value)}")
                return expression
            case FilterOperator.GT:
                return topk_field(field_name) > value
            case FilterOperator.LT:
                return topk_field(field_name) < value
            case FilterOperator.GE:
                return topk_field(field_name) >= value
            case FilterOperator.LE:
                return topk_field(field_name) <= value
            case FilterOperator.IN:
                raise FeatureNotSupportedException("IN is not yet supported")
            case FilterOperator.NOT_IN:
                raise FeatureNotSupportedException("NOT_IN is not yet supported")
            case _:
                raise NotImplementedException("Unsupported filter operator.", filter_operator=filter_operator)
