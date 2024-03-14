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

from typing import Generic, TypeVar

from superlinked.framework.common.exception import InitializationException
from superlinked.framework.common.interface.has_multiplier import HasMultiplier
from superlinked.framework.common.schema.exception import InvalidSchemaTypeException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaObject, String

# Referenced schema type
RST = TypeVar("RST")


class SchemaReference(String, HasMultiplier, Generic[RST]):
    """
    Schema reference used within an `EventSchema` to reference other schemas.
    """

    def __init__(
        self,
        name: str,
        schema_obj: SchemaObject,
        referenced_schema: type[RST],
    ) -> None:
        String.__init__(self, name, schema_obj)
        HasMultiplier.__init__(self)
        if not issubclass(referenced_schema, IdSchemaObject):
            raise InvalidSchemaTypeException(
                f"referenced_schema ({referenced_schema}) id not a subclass of IdSchemaObject"
            )
        self.__referenced_schema: type[IdSchemaObject] = referenced_schema

    @property
    def _referenced_schema(self) -> type[IdSchemaObject]:
        return self.__referenced_schema

    def __mul__(self, other: float | int) -> MultipliedSchemaReference:
        return MultipliedSchemaReference(self) * other

    def __rmul__(self, other: float | int) -> MultipliedSchemaReference:
        return MultipliedSchemaReference(self) * other


class MultipliedSchemaReference(HasMultiplier, Generic[RST]):
    def __init__(
        self, schema_reference: SchemaReference[RST], multiplier: float = 1.0
    ) -> None:
        super().__init__(multiplier)
        self.__validate_multiplier()
        self.schema_reference = schema_reference

    def __validate_multiplier(self) -> None:
        if self.multiplier == 0:
            raise InitializationException(
                f"{self.__class__.__name__} cannot have 0 (zero) as its multiplier."
            )

    def __mul__(self, other: float | int) -> MultipliedSchemaReference:
        multiplier = self.multiplier * other
        return MultipliedSchemaReference(self.schema_reference, multiplier)

    def __rmul__(self, other: float | int) -> MultipliedSchemaReference:
        return self * other
