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

from superlinked.framework.common.interface.comparison_operand import ComparisonOperand
from superlinked.framework.common.storage.field.field_data_type import FieldDataType


class Field(ComparisonOperand):
    def __init__(self, data_type: FieldDataType, name: str) -> None:
        super().__init__(Field)
        self.data_type = data_type
        self.name = name

    def __hash__(self) -> int:
        return hash((self.name, self.data_type))

    @staticmethod
    def _built_in_equal(left_operand: ComparisonOperand[Field], right_operand: object) -> bool:
        if isinstance(left_operand, Field) and isinstance(right_operand, Field):
            return right_operand.data_type == left_operand.data_type and right_operand.name == left_operand.name
        return False

    @staticmethod
    def _built_in_not_equal(left_operand: ComparisonOperand[Field], right_operand: object) -> bool:
        return not Field._built_in_equal(left_operand, right_operand)
