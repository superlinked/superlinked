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

import functools

from beartype.typing import Any


def lazy_property(fn) -> property:  # type: ignore
    attr_name = "_lazy_" + fn.__name__

    @property  # type: ignore
    @functools.wraps(fn)
    def _lazy_property(self) -> Any:  # type: ignore
        if not hasattr(self, attr_name):
            value = fn(self)
            setattr(self, attr_name, value)
        return getattr(self, attr_name)

    return _lazy_property  # type: ignore


def async_lazy_property(async_fn) -> property:  # type: ignore
    attr_name = "_lazy_" + async_fn.__name__

    @property  # type: ignore
    @functools.wraps(async_fn)
    async def _async_lazy_property(self) -> Any:  # type: ignore
        if not hasattr(self, attr_name):
            value = await async_fn(self)
            setattr(self, attr_name, value)
        return getattr(self, attr_name)

    return _async_lazy_property  # type: ignore
