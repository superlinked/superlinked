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

from superlinked.framework.dsl.query.predicate.binary_predicate import BinaryPredicate

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["EvaluatedBinaryPredicate"] = False


@dataclass
class EvaluatedBinaryPredicate:
    predicate: BinaryPredicate
    weight: float
    value: int | str | float | None
