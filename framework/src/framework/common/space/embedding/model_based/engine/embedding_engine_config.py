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

from typing_extensions import override

from superlinked.framework.common.precision import Precision


@dataclass(frozen=True, kw_only=True)
class EmbeddingEngineConfig:
    """
    Args:
        precision (Precision, optional): The desired precision (data type) for the embedding
            computation. Supported values include float32, float16. Defaults to Precision.FLOAT16.
    """

    precision: Precision = Precision.FLOAT16

    @override
    def __str__(self) -> str:
        return self.precision.name
