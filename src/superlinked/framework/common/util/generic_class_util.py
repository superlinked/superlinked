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

from beartype.typing import Any, Sequence, cast, get_args, get_origin

from superlinked.framework.common.schema.general_type import T


class GenericClassUtil:
    @staticmethod
    def if_not_class_get_origin(type_: type[T]) -> type:
        if inspect.isclass(type_):
            # For backward compatibility!
            if type_ in [list[str], list[float]]:
                return type_.__origin__
            return type_
        return cast(type, get_origin(type_))

    @staticmethod
    def get_generic_types(object_: Any) -> Sequence[Any]:
        generic_base_class = next(
            filter(
                lambda base_class: bool(get_args(base_class)),
                getattr(object_.__class__, "__orig_bases__", []),
            ),
            None,
        )
        if not generic_base_class:
            raise ValueError(
                f"{object_.__class__.__name__} does not have a Generic base class."
            )
        return get_args(generic_base_class)

    @staticmethod
    def get_single_generic_type(object_: Any) -> Any:
        return GenericClassUtil.get_generic_types(object_)[0]
