# Copyright 2025 Superlinked, Inc
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

from beartype.typing import Sequence


class MathUtil:
    @staticmethod
    def get_max_signed_sum(values: Sequence[int | float]) -> float:
        over_0 = sum(val for val in values if val > 0)
        below_0 = abs(sum(val for val in values if val < 0))
        return max(below_0, over_0)
