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
# pylint: disable=all


from beartype.typing import Any, Callable
from mypy.options import Options
from mypy.plugin import AttributeContext, Plugin
from mypy.types import Instance, NoneType, Type
from mypy.types import UnionType as MypyUnionType

# Pre-computed sets for faster lookups
SCHEMA_FIELD_TYPES = frozenset(
    {
        "superlinked.framework.common.schema.schema_object.Integer",
        "superlinked.framework.common.schema.schema_object.Float",
        "superlinked.framework.common.schema.schema_object.String",
        "superlinked.framework.common.schema.schema_object.Timestamp",
        "superlinked.framework.common.schema.schema_object.Blob",
        "superlinked.framework.common.schema.schema_object.Boolean",
        "superlinked.framework.common.schema.schema_object.FloatList",
        "superlinked.framework.common.schema.schema_object.StringList",
    }
)


# The base Schema class fullname
SCHEMA_BASE_CLASS = "superlinked.framework.common.schema.schema.Schema"


class SchemaFieldPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)
        # Cache for schema subclass checks to avoid repeated MRO traversals
        self._schema_subclass_cache: dict[str, bool] = {}
        # Cache for optional to mandatory SchemaField types to avoid repeated union processing
        self._type_transform_cache: dict[str, Type] = {}

    def get_attribute_hook(self, fullname: str) -> Callable[[AttributeContext], Type] | None:
        """
        Hook for attribute access during MyPy type checking.
        Transforms SchemaField | None → SchemaField.
        Called when MyPy encounters attribute access (e.g., obj.attr). The returned callable
        receives AttributeContext with:
        - ctx.type: Object type being accessed
        - ctx.default_attr_type: MyPy's inferred attribute type
        """
        # Only hook into attributes that could be schema fields
        # Skip obvious non-schema attributes
        if any(skip in fullname for skip in ("builtins.", "typing.", "collections.", "abc.")):
            return None

        return self._create_attribute_hook()

    def _create_attribute_hook(self) -> Callable[[AttributeContext], Type]:
        """Create attribute hook with access to plugin caches"""

        def schema_field_attribute_hook(ctx: AttributeContext) -> Type:
            return self._handle_attribute_access(ctx)

        return schema_field_attribute_hook

    def _is_schema_subclass(self, instance_type: Instance) -> bool:
        if not isinstance(instance_type, Instance):
            return False

        fullname = instance_type.type.fullname
        if fullname in self._schema_subclass_cache:
            return self._schema_subclass_cache[fullname]

        # Compute and cache the result
        result = self._compute_schema_subclass(instance_type)
        self._schema_subclass_cache[fullname] = result
        return result

    def _compute_schema_subclass(self, instance_type: Instance) -> bool:
        """Compute if instance is a schema subclass"""
        visited = set()

        def check_mro(type_info: Any) -> bool:
            if type_info.fullname in visited:
                return False
            visited.add(type_info.fullname)

            if type_info.fullname == SCHEMA_BASE_CLASS:
                return True

            # Check all base classes
            for base in type_info.bases:
                if isinstance(base, Instance) and check_mro(base.type):
                    return True
            return False

        return check_mro(instance_type.type)

    def _transform_union_type(self, union_type: MypyUnionType) -> Type:
        """Transform union type with caching"""
        # Create a simple cache key from union items
        cache_key = "|".join(str(item) for item in union_type.items)

        if cache_key in self._type_transform_cache:
            return self._type_transform_cache[cache_key]

        # Find schema field and None types
        schema_field_type: Type | MypyUnionType | None = None
        has_none = False

        for item in union_type.items:
            if isinstance(item, Instance) and item.type.fullname in SCHEMA_FIELD_TYPES:
                schema_field_type = item
            elif isinstance(item, NoneType):
                has_none = True

        # Transform SchemaField | None to SchemaField
        result = schema_field_type if (schema_field_type and has_none) else union_type
        self._type_transform_cache[cache_key] = result
        return result

    def _handle_attribute_access(self, ctx: AttributeContext) -> Type:
        """Handle attribute access with optimizations"""
        # Quick check: only process if we have type context
        if not (hasattr(ctx, "type") and isinstance(ctx.type, Instance)):
            return ctx.default_attr_type

        # Check if it's a schema subclass (cached)
        if not self._is_schema_subclass(ctx.type):
            return ctx.default_attr_type

        # Only process union types
        if not isinstance(ctx.default_attr_type, MypyUnionType):
            return ctx.default_attr_type

        # Transform with caching
        return self._transform_union_type(ctx.default_attr_type)


def plugin(version: str) -> type[SchemaFieldPlugin]:
    return SchemaFieldPlugin
