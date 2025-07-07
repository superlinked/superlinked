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

from altair import value
from beartype.typing import Any, cast, Mapping
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
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.query_clause.single_value_param_query_clause import (
    SingleValueParamQueryClause,
    VALUE_PARAM_FIELD,
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
        
        if self.op == ComparisonOperationType.RANGE:
            annotation = "".join(
                (
                    f"  - {value_param.name}: A tuple of ({value_accepted_type.__name__} | None, {value_accepted_type.__name__} | None) "
                    f"that represents the range (min_value, max_value) for the `{self.operand.name}` field.",
                    f"\n    - **Possible values:** {options}." if options else "",
                    f"\n    - **Description:** {description}" if description else "",
                )
            )
        else:
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
        elif operation._op == ComparisonOperationType.RANGE:
            # For range operations, expect a tuple of (min_value, max_value)
            param_type = tuple
        elif operation._op == ComparisonOperationType.GEO_BOX:
            # For geo bounding box operations, expect a dict
            param_type = dict
        elif operation._op == ComparisonOperationType.GEO_RADIUS:
            # For geo radius operations, expect a dict
            param_type = dict
        elif operation._op == ComparisonOperationType.GEO_POLYGON:
            # For geo polygon operations, expect a dict
            param_type = dict
        
        return HardFilterClause(
            QueryClause._to_typed_param(operation._other, [param_type]),
            operation._op,
            schema_field,
            operation._group_key,
        )

    @override
    def _evaluate_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        if self.op == ComparisonOperationType.RANGE:
            # Special handling for RANGE operations to resolve tuple parameters
            return self._evaluate_range_changes(params_values, is_override_set)
        elif self.op == ComparisonOperationType.GEO_BOX:
            # Special handling for GEO_BOX operations to resolve nested parameters
            return self._evaluate_geo_box_changes(params_values, is_override_set)
        elif self.op == ComparisonOperationType.GEO_RADIUS:
            # Special handling for GEO_RADIUS operations to resolve nested parameters
            return self._evaluate_geo_radius_changes(params_values, is_override_set)
        elif self.op == ComparisonOperationType.GEO_POLYGON:
            # Special handling for GEO_POLYGON operations to resolve nested parameters
            return self._evaluate_geo_polygon_changes(params_values, is_override_set)
        else:
            # Default behavior for other operations
            return super()._evaluate_changes(params_values, is_override_set)
    
    def _evaluate_range_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        """
        Special parameter resolution for RANGE operations.
        Resolves range parameters from provided values, handling optional min/max parameters.
        Uses the actual range parameter objects to determine the correct parameter names.
        """
        # For range operations, we need to build a tuple (min_value, max_value) from the provided parameters
        # Range parameters can be optional - if not provided, they should be None
        
        # Get the actual value (which should be a list/tuple of parameter objects for range operations)
        value = self._get_value()
        
        value_list = list(value)
        min_value, max_value = value_list
        
        # Assume first object is min, second is max
        if len(value_list) >= 1 and hasattr(value_list[0], 'name'):
            min_param_name = value_list[0].name
            min_value = params_values.get(min_param_name, None)

        if len(value_list) >= 2 and hasattr(value_list[1], 'name'):
            max_param_name = value_list[1].name
            max_value = params_values.get(max_param_name, None)
        
        resolved_tuple = (min_value, max_value)
        
        # Create an evaluated parameter with the resolved tuple
        param_to_alter = QueryClause.get_typed_param(self.value_param)
        resolved_param = param_to_alter.evaluate(resolved_tuple)
        return {VALUE_PARAM_FIELD: resolved_param}
    
    def _evaluate_geo_box_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        """
        Special parameter resolution for GEO_BOX operations.
        Resolves the nested dictionary of sl.Param objects to actual values.
        """
        # We know the geo parameters we need
        geo_param_names = ["min_lat", "max_lat", "min_lon", "max_lon"]
        
        if not set(geo_param_names).issubset(params_values.keys()):
            return super()._evaluate_changes(params_values, is_override_set)

        resolved_dict = {param_name: params_values[param_name] for param_name in geo_param_names}
        
        param_to_alter = QueryClause.get_typed_param(self.value_param)
        resolved_param = param_to_alter.evaluate(resolved_dict)
        return {VALUE_PARAM_FIELD: resolved_param}

    def _evaluate_geo_radius_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        """
        Special parameter resolution for GEO_RADIUS operations.
        Resolves the nested dictionary of sl.Param objects to actual values.
        """
        # We know the geo parameters we need
        geo_param_names = ["center_lat", "center_lon", "radius"]
        
        if not set(geo_param_names).issubset(params_values.keys()):
            return super()._evaluate_changes(params_values, is_override_set)

        resolved_dict = {param_name: params_values[param_name] for param_name in geo_param_names}
        
        param_to_alter = QueryClause.get_typed_param(self.value_param)
        resolved_param = param_to_alter.evaluate(resolved_dict)
        return {VALUE_PARAM_FIELD: resolved_param}

    def _evaluate_geo_polygon_changes(self, params_values: Mapping[str, ParamInputType], is_override_set: bool) -> dict[str, Any]:
        """
        Special parameter resolution for GEO_POLYGON operations.
        Resolves the list of coordinate pairs to actual values.
        """
        # For polygon operations, we expect the "polygon" parameter to contain a list of coordinate pairs
        if "polygon" not in params_values:
            return super()._evaluate_changes(params_values, is_override_set)

        polygon_coords = params_values["polygon"]
        
        # Wrap the polygon coordinates in a dictionary as expected by GeoPolygonFilter
        resolved_dict = {"polygon": polygon_coords}
        
        # Create an evaluated parameter with the resolved polygon coordinates
        param_to_alter = QueryClause.get_typed_param(self.value_param)
        resolved_param = param_to_alter.evaluate(resolved_dict)
        return {VALUE_PARAM_FIELD: resolved_param}


