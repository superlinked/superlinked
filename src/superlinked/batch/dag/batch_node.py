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

from abc import ABC, abstractmethod
from typing import Generic

from pyspark.sql import DataFrame

from superlinked.framework.common.dag.node import NT


class BatchNode(ABC, Generic[NT]):
    def __init__(
        self,
        node: NT,
    ) -> None:
        self.node = node

    @abstractmethod
    def transform(self, df: DataFrame) -> DataFrame:
        pass
