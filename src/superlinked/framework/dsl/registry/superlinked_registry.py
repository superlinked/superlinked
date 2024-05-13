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

from superlinked.framework.dsl.executor.runnable import Runnable
from superlinked.framework.dsl.registry.exception import DuplicateRunnablesException


class SuperlinkedRegistry:
    __registry: set[Runnable] = set()

    @staticmethod
    def register(*items: Runnable) -> None:
        for item in items:
            if item in SuperlinkedRegistry.__registry:
                raise DuplicateRunnablesException(
                    f"Runnable {item} already registered!"
                )
            SuperlinkedRegistry.__registry.add(item)

    @staticmethod
    def registered_items() -> frozenset[Runnable]:
        return frozenset(SuperlinkedRegistry.__registry)
