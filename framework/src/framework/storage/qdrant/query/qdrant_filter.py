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


from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from beartype.typing import cast, Any
from qdrant_client.models import FieldCondition, MatchAny, MatchValue, Range, GeoBoundingBox, GeoRadius, GeoPolygon
from typing_extensions import override

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field.field import Field
from superlinked.framework.common.storage.field.field_data import FieldData
from superlinked.framework.common.storage.field.field_data_type import FieldDataType
from superlinked.framework.common.util.math_util import MathUtil
from superlinked.framework.storage.qdrant.qdrant_field_encoder import QdrantFieldEncoder


class ClauseType(Enum):
    MUST = "must"
    MUST_NOT = "must_not"


@dataclass(frozen=True)
class QdrantFilter(ABC):
    clause_type: ClauseType

    @abstractmethod
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        pass

    def valid_types_string(self, valid_types: tuple[type, ...]) -> str:
        return ", ".join([t.__name__ for t in valid_types])


@dataclass(frozen=True)
class MatchValueFilter(QdrantFilter):
    valid_types = (bool, int, str)

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_value_filter(filter_, encoder),
            )
        ]

    def _encode_match_value_filter(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> MatchValue:
        other = MathUtil.convert_float_typed_integers_to_int(filter_._other)
        if not isinstance(other, MatchValueFilter.valid_types):
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchValueFilter.valid_types)} "
                + f"{MatchValue.__name__}, got {type(other)}"
            )
        return MatchValue(value=encoder.encode_field(FieldData.from_field(cast(Field, filter_._operand), other)))


@dataclass(frozen=True)
class MatchAnyFilter(QdrantFilter):
    valid_types = (int, str)

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_any_filter(filter_, encoder),
            )
        ]

    def _encode_match_any_filter(self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder) -> MatchAny:
        unconverted_others = filter_._other if isinstance(filter_._other, list) else [filter_._other]
        others = [MathUtil.convert_float_typed_integers_to_int(other) for other in unconverted_others]
        if invalid_any := [
            type(other).__name__ for other in others if not isinstance(other, MatchAnyFilter.valid_types)
        ]:
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchAnyFilter.valid_types)} "
                + f"{MatchAny.__name__}, got {invalid_any}"
            )
        field = cast(Field, filter_._operand)
        filter_values = [encoder.encode_field(self._create_field_data(field, other)) for other in others]
        return MatchAny(any=filter_values)

    def _create_field_data(self, field: Field, value: object) -> FieldData:
        if field.data_type == FieldDataType.STRING_LIST:
            return FieldData(FieldDataType.STRING, field.name, value)
        return FieldData.from_field(field, value)


@dataclass(frozen=True)
class MatchRangeFilter(QdrantFilter):
    valid_types = (float, int)
    range_arg_name_by_op_type = {
        ComparisonOperationType.GREATER_THAN: "gt",
        ComparisonOperationType.LESS_THAN: "lt",
        ComparisonOperationType.GREATER_EQUAL: "gte",
        ComparisonOperationType.LESS_EQUAL: "lte",
    }

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                range=self._encode_range_filter(filter_, encoder),
            )
        ]

    def _encode_range_filter(self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder) -> Range:
        if not isinstance(filter_._other, MatchRangeFilter.valid_types):
            raise ValueError(
                f"Qdrant only supports {self.valid_types_string(MatchRangeFilter.valid_types)} "
                + f"{MatchValue.__name__}, got {type(filter_._other)}"
            )
        range_args = {
            MatchRangeFilter.range_arg_name_by_op_type[filter_._op]: encoder.encode_field(
                FieldData.from_field(cast(Field, filter_._operand), filter_._other)
            )
        }
        return Range(**range_args)


@dataclass(frozen=True)
class ContainsAllFilter(MatchAnyFilter):
    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        other = filter_._other if isinstance(filter_._other, list) else [filter_._other]
        filter_per_other = [filter_._operand.contains_all(o) for o in other]
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                match=self._encode_match_any_filter(filter_, encoder),
            )
            for filter_ in filter_per_other
        ]


@dataclass(frozen=True)
class RangeFilter(QdrantFilter):
    valid_types = (float, int)

    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        return [
            FieldCondition(
                key=cast(Field, filter_._operand).name,
                range=self._encode_range_filter(filter_, encoder),
            )
        ]

    def _encode_range_filter(self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder) -> Range:
        if not isinstance(filter_._other, tuple) or len(filter_._other) != 2:
            raise ValueError("Range operation requires a tuple (min_value, max_value)")
        
        # Safely extract min and max values
        min_val, max_val = filter_._other

        if min_val is not None and not isinstance(min_val, RangeFilter.valid_types):
            raise ValueError(
                f"Qdrant range min value only supports {self.valid_types_string(RangeFilter.valid_types)}, got {type(min_val)}"
            )
        
        if max_val is not None and not isinstance(max_val, RangeFilter.valid_types):
            raise ValueError(
                f"Qdrant range max value only supports {self.valid_types_string(RangeFilter.valid_types)}, got {type(max_val)}"
            )
        
        field = cast(Field, filter_._operand)
        range_args = {}
        
        if min_val is not None:
            range_args["gte"] = encoder.encode_field(FieldData.from_field(field, min_val))
        
        if max_val is not None:
            range_args["lte"] = encoder.encode_field(FieldData.from_field(field, max_val))
        
        return Range(**range_args)


@dataclass(frozen=True)
class GeoBoxFilter(QdrantFilter):
    """
    Implementation of geo bounding box filter for Qdrant.
    This filter allows searching for points within a geographic bounding box.
    """
    
    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        """
        Convert ComparisonOperation to Qdrant's FieldCondition with GeoBoundingBox.
        
        Args:
            filter_: The comparison operation containing the bounding box parameters
            encoder: The field encoder to use for encoding values
            
        Returns:
            A list containing a single FieldCondition with GeoBoundingBox filter
        """
        # Get the bounding box parameters from filter_._other
        # Expected format: {"min_lat": value, "max_lat": value, "min_lon": value, "max_lon": value}
        field_name = cast(Field, filter_._operand).name
        geo_params = filter_._other
        
        # Validate that we have a dictionary with required parameters
        if not isinstance(geo_params, dict):
            raise ValueError(f"GeoBoxFilter expects a dict of parameters, got: {type(geo_params)}")
        
        required_keys = {"min_lat", "max_lat", "min_lon", "max_lon"}
        if not required_keys.issubset(geo_params.keys()):
            raise ValueError(f"GeoBoxFilter expects parameters: {required_keys}, got: {set(geo_params.keys())}")
        
        min_lat = geo_params["min_lat"]
        max_lat = geo_params["max_lat"]
        min_lon = geo_params["min_lon"]
        max_lon = geo_params["max_lon"]
        
        # Check if any of the parameters are still unresolved Param objects
        # If so, skip this filter by returning empty list
        if not self._are_valid_numeric_values(min_lat, max_lat, min_lon, max_lon):
            return []
        
        # Convert the filter to a Qdrant GeoBoundingBox condition
        return [
            FieldCondition(
                key=field_name,
                geo_bounding_box=self._create_geo_bounding_box(min_lat, max_lat, min_lon, max_lon)
            )
        ]
    
    def _are_valid_numeric_values(self, min_lat: Any, max_lat: Any, min_lon: Any, max_lon: Any) -> bool:
        """
        Check if all the geo box parameters are valid numeric values.
        
        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            
        Returns:
            True if all values are valid numbers, False otherwise
        """
        valid_types = (int, float)
        return (
            isinstance(min_lat, valid_types) and
            isinstance(max_lat, valid_types) and
            isinstance(min_lon, valid_types) and
            isinstance(max_lon, valid_types)
        )
    
    def _create_geo_bounding_box(self, min_lat: Any, max_lat: Any, min_lon: Any, max_lon: Any) -> GeoBoundingBox:
        """
        Create a Qdrant GeoBoundingBox from the provided bounding box parameters.
        
        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude 
            max_lon: Maximum longitude
            
        Returns:
            GeoBoundingBox object for Qdrant filtering
        """
        return GeoBoundingBox(
            top_left={"lat": max_lat, "lon": min_lon},
            bottom_right={"lat": min_lat, "lon": max_lon}
        )


@dataclass(frozen=True)
class GeoRadiusFilter(QdrantFilter):
    """
    Implementation of geo radius filter for Qdrant.
    This filter allows searching for points within a specified radius from a center point.
    """
    
    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        """
        Convert ComparisonOperation to Qdrant's FieldCondition with GeoRadius.
        
        Args:
            filter_: The comparison operation containing the radius parameters
            encoder: The field encoder to use for encoding values
            
        Returns:
            A list containing a single FieldCondition with GeoRadius filter
        """
        # Get the radius parameters from filter_._other
        # Expected format: {"center_lat": value, "center_lon": value, "radius": value}
        field_name = cast(Field, filter_._operand).name
        geo_params = filter_._other
        
        # Validate that we have a dictionary with required parameters
        if not isinstance(geo_params, dict):
            raise ValueError(f"GeoRadiusFilter expects a dict of parameters, got: {type(geo_params)}")
        
        required_keys = {"center_lat", "center_lon", "radius"}
        if not required_keys.issubset(geo_params.keys()):
            raise ValueError(f"GeoRadiusFilter expects parameters: {required_keys}, got: {set(geo_params.keys())}")
        
        center_lat = geo_params["center_lat"]
        center_lon = geo_params["center_lon"]
        radius = geo_params["radius"]
        
        # Check if any of the parameters are still unresolved Param objects
        # If so, skip this filter by returning empty list
        if not self._are_valid_numeric_values(center_lat, center_lon, radius):
            return []
        
        # Convert the filter to a Qdrant GeoRadius condition
        return [
            FieldCondition(
                key=field_name,
                geo_radius=self._create_geo_radius(center_lat, center_lon, radius)
            )
        ]
    
    def _are_valid_numeric_values(self, center_lat: Any, center_lon: Any, radius: Any) -> bool:
        """
        Check if all the geo radius parameters are valid numeric values.
        
        Args:
            center_lat: Center point latitude
            center_lon: Center point longitude  
            radius: Radius value
            
        Returns:
            True if all values are valid numbers, False otherwise
        """
        valid_types = (int, float)
        return (
            isinstance(center_lat, valid_types) and
            isinstance(center_lon, valid_types) and
            isinstance(radius, valid_types)
        )
    
    def _create_geo_radius(self, center_lat: Any, center_lon: Any, radius: Any) -> GeoRadius:
        """
        Create a Qdrant GeoRadius from the provided radius parameters.
        
        Args:
            center_lat: Center point latitude
            center_lon: Center point longitude
            radius: Radius in meters
            
        Returns:
            GeoRadius object for Qdrant filtering
        """
        return GeoRadius(
            center={"lat": center_lat, "lon": center_lon},
            radius=radius
        )


@dataclass(frozen=True)
class GeoPolygonFilter(QdrantFilter):
    """
    Implementation of geo polygon filter for Qdrant.
    This filter allows searching for points within a specified polygon area.
    """
    
    @override
    def to_field_conditions(
        self, filter_: ComparisonOperation[Field], encoder: QdrantFieldEncoder
    ) -> list[FieldCondition]:
        """
        Convert ComparisonOperation to Qdrant's FieldCondition with GeoPolygon.
        
        Args:
            filter_: The comparison operation containing the polygon parameters
            encoder: The field encoder to use for encoding values
            
        Returns:
            A list containing a single FieldCondition with GeoPolygon filter
        """
        # Get the polygon parameters from filter_._other
        # Expected format: {"polygon": [[lon1, lat1], [lon2, lat2], ..., [lon1, lat1]]}
        field_name = cast(Field, filter_._operand).name
        geo_params = filter_._other
        
        # Validate that we have a dictionary with required parameters
        if not isinstance(geo_params, dict):
            raise ValueError(f"GeoPolygonFilter expects a dict of parameters, got: {type(geo_params)}")
        
        if "polygon" not in geo_params:
            raise ValueError("GeoPolygonFilter expects 'polygon' parameter")
        
        polygon_coords = geo_params["polygon"]
        
        # Check if any of the coordinates are still unresolved Param objects
        # If so, skip this filter by returning empty list
        if not self._are_valid_polygon_coordinates(polygon_coords):
            return []
        
        # Convert the filter to a Qdrant GeoPolygon condition
        geo_polygon = self._create_geo_polygon(polygon_coords)
        
        field_condition = FieldCondition(
            key=field_name,
            geo_polygon=geo_polygon
        )
        
        return [field_condition]
    
    def _are_valid_polygon_coordinates(self, polygon_coords: Any) -> bool:
        """
        Check if the polygon coordinates are valid.
        
        Args:
            polygon_coords: List of coordinate pairs
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        if not isinstance(polygon_coords, list) or len(polygon_coords) < 3:
            return False
        
        valid_types = (int, float)
        for coord_pair in polygon_coords:
            if not isinstance(coord_pair, list) or len(coord_pair) != 2:
                return False
            lon, lat = coord_pair
            if not (isinstance(lon, valid_types) and isinstance(lat, valid_types)):
                return False
        
        return True
    
    def _create_geo_polygon(self, polygon_coords: Any) -> GeoPolygon:
        """
        Create a Qdrant GeoPolygon from the provided polygon coordinates.
        
        Args:
            polygon_coords: List of [longitude, latitude] coordinate pairs
            
        Returns:
            GeoPolygon object for Qdrant filtering
        """
        # Convert coordinates to the format Qdrant expects
        # Qdrant expects: {"exterior": {"points": [{"lat": lat, "lon": lon}, ...]}}
        exterior_points = []
        for coord_pair in polygon_coords:
            lon, lat = coord_pair
            exterior_points.append({"lat": lat, "lon": lon})
        
        return GeoPolygon(exterior={"points": exterior_points})
