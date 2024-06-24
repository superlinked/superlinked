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

import uuid
from dataclasses import dataclass, field

from beartype.typing import Generic, TypeVar

from superlinked.framework.common.data_types import PythonTypes

# EvaluationResultType
ERT = TypeVar("ERT", bound=PythonTypes)


@dataclass(frozen=True)
class SingleEvaluationResult(Generic[ERT]):
    node_id: str
    value: ERT
    _object_id: str | None = None

    @property
    def object_id(self) -> str:
        return self._object_id or str(uuid.uuid4())


@dataclass(frozen=True)
class EvaluationResult(Generic[ERT]):
    main: SingleEvaluationResult[ERT]
    chunks: list[SingleEvaluationResult[ERT]] = field(default_factory=list)
