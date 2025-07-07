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


from beartype.typing import Any

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    LIST_TYPE_COMPATIBLE_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.util.generic_class_util import GenericClassUtil
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.query.param import Param


class QueryFilterValidator:

    @staticmethod
    def validate_operation_operand_type(comparison_operation: ComparisonOperation, allow_param: bool) -> None:
        # Skip validation for GEO_BOX, GEO_RADIUS, and GEO_POLYGON operations as they have custom format
        if comparison_operation._op in [ComparisonOperationType.GEO_BOX, ComparisonOperationType.GEO_RADIUS, ComparisonOperationType.GEO_POLYGON]:
            return
            
        expected_type = GenericClassUtil.get_single_generic_type_extended(comparison_operation._operand)
        if comparison_operation._op in LIST_TYPE_COMPATIBLE_TYPES:
            QueryFilterValidator._validate_list_type(comparison_operation, expected_type, allow_param)
        elif comparison_operation._op == ComparisonOperationType.RANGE:
            QueryFilterValidator._validate_range_type(comparison_operation, expected_type, allow_param)
        else:
            QueryFilterValidator._validate_single_type(comparison_operation, expected_type, allow_param)

    @staticmethod
    def validate_operation_is_supported(comparison_operation: ComparisonOperation[SchemaField]) -> None:
        field = QueryFilterValidator.__get_schema_field(comparison_operation)
        if comparison_operation._op not in field.supported_comparison_operation_types:
            raise QueryException(f"Field {field.name} doesn't support {comparison_operation._op.value} operation.")

    @staticmethod
    def validate_operation_field_is_part_of_schema(
        comparison_operation: ComparisonOperation[SchemaField], schema: IdSchemaObject
    ) -> None:
        field = QueryFilterValidator.__get_schema_field(comparison_operation)
        if field.schema_obj != schema:
            raise QueryException(
                f"{field.schema_obj._schema_name}.{field.name} is not part of the {schema._schema_name} schema."
            )

    @staticmethod
    def __get_schema_field(comparison_operation: ComparisonOperation) -> SchemaField:
        field = comparison_operation._operand
        if not isinstance(field, SchemaField):
            raise QueryException("ComparisonOperation operand must be a SchemaField")
        return field

    @staticmethod
    def _validate_range_type(comparison_operation: ComparisonOperation, expected_type: Any, allow_param: bool) -> None:
        other = comparison_operation._other
        if allow_param and isinstance(other, Param):
            return

        if not isinstance(other, tuple) or len(other) != 2:
            raise QueryException("Range operation requires a tuple (min_value, max_value).")
        
        min_val, max_val = other
        
        # Validate min_value type (can be None, Param, or expected_type)
        if min_val is not None and not isinstance(min_val, Param) and not isinstance(min_val, expected_type):
            raise QueryException(
                f"Range min_value type mismatch: expected {expected_type.__name__} or None, got {type(min_val).__name__}."
            )
        
        # Validate max_value type (can be None, Param, or expected_type)
        if max_val is not None and not isinstance(max_val, Param) and not isinstance(max_val, expected_type):
            raise QueryException(
                f"Range max_value type mismatch: expected {expected_type.__name__} or None, got {type(max_val).__name__}."
            )

    @staticmethod
    def _validate_list_type(comparison_operation: ComparisonOperation, expected_type: Any, allow_param: bool) -> None:
        other = comparison_operation._other
        if allow_param and isinstance(other, Param):
            return

        # Map to base type for list-type fields - list[str] -> str
        if isinstance(expected_type(), list) and TypeValidator.is_sequence_safe(other):
            expected_type = expected_type.__args__[0]
            TypeValidator.validate_list_item_type(other, expected_type, "filter operand")

    @staticmethod
    def _validate_single_type(
        comparison_operation: ComparisonOperation,
        expected_type: type,
        allow_param: bool,
    ) -> None:
        if allow_param and isinstance(comparison_operation._other, Param):
            return

        if not isinstance(comparison_operation._other, expected_type):
            allowed_types_text = " or ".join(
                [allowed_type.__name__ for allowed_type in ([expected_type] + ([Param] if allow_param else []))]
            )
            unsupported_type_text = type(comparison_operation._other).__name__
            raise QueryException(
                f"Unsupported filter operand type: {unsupported_type_text}, expected {allowed_types_text}."
            )
