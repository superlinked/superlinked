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

import inspect
from typing import get_origin

from superlinked.framework.common.schema.general_type import T


class SchemaUtil:
    @staticmethod
    def if_not_class_get_origin(type_: type[T]) -> type | None:
        if inspect.isclass(type_):
            return type_
        return get_origin(type_)
