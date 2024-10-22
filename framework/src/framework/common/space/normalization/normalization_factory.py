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


from beartype.typing import Any, Mapping

from superlinked.framework.common.space.config.normalization.normalization_config import (
    ConstantNormConfig,
    L2NormConfig,
    NoNormConfig,
    NormalizationConfig,
)
from superlinked.framework.common.space.normalization.normalization import (
    ConstantNorm,
    L2Norm,
    NoNorm,
    Normalization,
)

NORMALIZATION_BY_TYPE: Mapping[type[NormalizationConfig], type[Normalization]] = {
    L2NormConfig: L2Norm,
    ConstantNormConfig: ConstantNorm,
    NoNormConfig: NoNorm,
}


class NormalizationFactory:
    @staticmethod
    def create_normalization(
        normalization_config: NormalizationConfig,
    ) -> Normalization[Any]:
        if normalization_class := NORMALIZATION_BY_TYPE.get(type(normalization_config)):
            return normalization_class(normalization_config)
        raise ValueError(
            f"Unknown normalization config type: {type(normalization_config)}"
        )
