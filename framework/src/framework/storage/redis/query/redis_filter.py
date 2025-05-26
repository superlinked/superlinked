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
from redisvl.query.filter import FilterExpression, FilterOperator, Num, Tag, Text

from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.storage.query.vdb_filter import VDBFilter
from superlinked.framework.storage.redis.query.redis_filter_information import (
    RedisFilterInformation,
)

REDIS_FIELD_TYPE_BY_FIELD_DATA_TYPE: dict[FieldDataType, type[Num | Tag | Text]] = {
    FieldDataType.INT: Num,
    FieldDataType.DOUBLE: Num,
    FieldDataType.STRING: Tag,
    FieldDataType.METADATA_STRING: Tag,
    FieldDataType.STRING_LIST: Tag,
    FieldDataType.BOOLEAN: Tag,
}
REDIS_FIELD_TYPES_TO_BE_MAPPED_TO_LIST = [FieldDataType.STRING, FieldDataType.METADATA_STRING, FieldDataType.BOOLEAN]


@dataclass(frozen=True)
class RedisFilter(VDBFilter):
    def __init__(self, field: Field, field_value: Any, op: ComparisonOperationType) -> None:
        if field.data_type in REDIS_FIELD_TYPES_TO_BE_MAPPED_TO_LIST:
            field_value = [field_value]
        super().__init__(field=field, field_value=field_value, op=op)

    def to_expression(self) -> FilterExpression:
        filter_info = RedisFilterInformation.get(self.op)
        values = filter_info.get_value_mapper_fn()(self.field_value)
        filter_expressions = [
            self._calculate_expression(self.field, filter_info.filter_operator, value) for value in values
        ]
        combined_expression = filter_info.get_combination_fn()(filter_expressions)
        return combined_expression

    @classmethod
    def _calculate_expression(cls, field: Field, filter_operator: FilterOperator, value: Any) -> FilterExpression:
        redis_field = cls._init_filter_field(field)
        redis_field._set_value(value, redis_field.SUPPORTED_VAL_TYPES, filter_operator)
        return FilterExpression(str(redis_field))

    @classmethod
    def _init_filter_field(cls, field: Field) -> Num | Tag | Text:
        if redis_field_type := REDIS_FIELD_TYPE_BY_FIELD_DATA_TYPE.get(field.data_type):
            return redis_field_type(field.name)
        raise NotImplementedError(f"Unsupported {FieldDataType.__name__}: {field.data_type}")
