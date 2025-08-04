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

from beartype.typing import Sequence, cast

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.common.schema.event_schema_object import CreatedAtField
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.index.effect import Effect
from superlinked.framework.dsl.space.space import Space


class IndexValidator:
    @staticmethod
    def validate_spaces(spaces: Space | Sequence[Space]) -> list[Space]:
        normalized_spaces = list(spaces) if isinstance(spaces, Sequence) else [spaces]
        IndexValidator._ensure_not_empty(normalized_spaces, "Index must be built on at least 1 space.")
        IndexValidator._ensure_no_duplicates(normalized_spaces, "Index cannot contain duplicate spaces.")
        return normalized_spaces

    @staticmethod
    def validate_fields(fields: SchemaField | Sequence[SchemaField | None] | None) -> Sequence[SchemaField]:
        if fields is None:
            return []
        if not isinstance(fields, Sequence):
            return [fields]
        IndexValidator._ensure_no_none_values(fields, "Fields cannot contain None values")
        return cast(Sequence[SchemaField], fields)

    @staticmethod
    def validate_fields_to_exclude(
        fields_to_exclude: SchemaField | Sequence[SchemaField | None] | None,
    ) -> Sequence[SchemaField]:
        if fields_to_exclude is None:
            return []
        if not isinstance(fields_to_exclude, Sequence):
            return [fields_to_exclude]
        IndexValidator._ensure_no_none_values(fields_to_exclude, "Fields to exclude cannot contain None values.")
        normalized_fields = cast(Sequence[SchemaField], fields_to_exclude)
        IndexValidator._ensure_no_restricted_field_types(
            normalized_fields,
            {IdField: "Id field cannot be excluded.", CreatedAtField: "Created at field cannot be excluded."},
        )
        return normalized_fields

    @staticmethod
    def validate_effects(effects: Effect | Sequence[Effect] | None, spaces: Sequence[Space]) -> list[Effect]:
        if effects is None:
            return []
        normalized_effects = list(effects) if isinstance(effects, Sequence) else [effects]
        IndexValidator._ensure_effects_use_valid_spaces(normalized_effects, spaces)
        return normalized_effects

    @staticmethod
    def _ensure_not_empty(items: Sequence, message: str) -> None:
        if len(items) == 0:
            raise InvalidInputException(message)

    @staticmethod
    def _ensure_no_duplicates(items: Sequence, message: str) -> None:
        if len(set(items)) != len(items):
            raise InvalidInputException(message)

    @staticmethod
    def _ensure_no_none_values(items: Sequence, message: str) -> None:
        if None in items:
            raise InvalidInputException(message)

    @staticmethod
    def _ensure_no_restricted_field_types(fields: Sequence[SchemaField], restricted_types: dict[type, str]) -> None:
        field_types = {type(field) for field in fields}
        for restricted_type, error_message in restricted_types.items():
            if restricted_type in field_types:
                raise InvalidInputException(error_message)

    @staticmethod
    def _ensure_effects_use_valid_spaces(effects: Sequence[Effect], spaces: Sequence[Space]) -> None:
        invalid_space_effects = [effect for effect in effects if effect.space not in spaces]
        if invalid_space_effects:
            raise InvalidInputException(f"Effects must work on the Index's spaces, got ({invalid_space_effects})")
