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


from collections.abc import Sequence

from typing_extensions import override

from superlinked.framework.common.interface.comparison_operation_type import (
    EQUALITY_COMPARISON_OPERATION_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.schema.schema_object import SchemaField, SchemaObjectT

ID_FIELD_NAME = "id"


class IdField(SchemaField[str]):
    """
    A class representing the ID field of a schema.
    """

    def __init__(self, schema_obj: SchemaObjectT, id_field_name: str) -> None:
        super().__init__(id_field_name, schema_obj, str, nullable=False)

    @property
    @override
    def supported_comparison_operation_types(self) -> Sequence[ComparisonOperationType]:
        return EQUALITY_COMPARISON_OPERATION_TYPES
