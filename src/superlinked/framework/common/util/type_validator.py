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

from beartype import BeartypeConf, beartype
from beartype.typing import Any, Callable, TypeAlias, TypeVar
from beartype.vale import Is
from beartype.vale._core._valecore import BeartypeValidator

# WrapableType
WT = TypeVar(
    "WT",
    bound=type | classmethod | staticmethod | property | Callable[..., Any],
)

# KeyType
KT = TypeVar("KT")
# ValueType
VT = TypeVar("VT")
# ListType
LIT = TypeVar("LIT")


class TypeValidator:
    @staticmethod
    def validate_list_item_type(
        items: Any,
        type_: type | TypeAlias,
        items_name: str,
    ) -> None:
        """
        Checks if `items` is a list and, if it is, all elements of it is of the type `type_`.
        Raises:
            TypeError: if either of the checks fails.
        """
        if not isinstance(items, list):
            raise TypeError(
                f"'{items_name}' must be a `list`, got {items.__class__.__name__}"
            )
        if items_of_wrong_type := [
            item for item in items if not isinstance(item, type_)
        ]:
            raise TypeError(
                f"'{items_name}' must be a(n) "
                + f"{type_.__name__}` list, got {items_of_wrong_type}"
            )

    @staticmethod
    def validate_dict_item_type(
        item: Any,
        key_type: type | TypeAlias,
        value_type: type | TypeAlias,
        item_name: str,
        is_none_valid: bool = False,
    ) -> None:
        """
        Checks if `item` is a dictionary and, if it is,
            all keys and values are of the types `key_type` and `value_type` respectively.
        Raises:
            TypeError: if either of the checks fails.
        """
        if item is None and is_none_valid:
            return
        if not isinstance(item, dict):
            raise TypeError(
                f"'{item_name}' must be {'`None` or ' if is_none_valid else ''}"
                + f"a `dict`, got {item.__class__.__name__}"
            )
        if item and (
            items_of_wrong_type := {
                k: v
                for k, v in item.items()
                if not isinstance(k, key_type) or not isinstance(v, value_type)
            }
        ):
            raise TypeError(
                f"'{item_name}' must be {'`None` or ' if is_none_valid else ''}"
                + f"a map from `{key_type.__name__}` to "
                + f"`{value_type.__name__}`, got {items_of_wrong_type}"
            )

    @staticmethod
    def wrap(
        obj: WT, conf: BeartypeConf = BeartypeConf(violation_param_type=TypeError)
    ) -> WT:
        """
        Turns the class or callable into a dynamically type-checked object.
        """
        return beartype(conf=conf)(obj)

    @staticmethod
    def list_validator(type_: type[LIT]) -> BeartypeValidator:
        """
        Returns a beartype-compliant validator for lists, which checks if
            the annotated object is a list and, if it is, all elements of it is of the type `type_`.
        """

        def validator(item_list: Any) -> bool:
            return isinstance(item_list, list) and all(
                isinstance(item, type_) for item in item_list
            )

        return Is[validator]

    @staticmethod
    def dict_validator(key_type: type[KT], value_type: type[VT]) -> BeartypeValidator:
        """
        Returns a beartype-compliant validator for dictionaries, which checks if
            the annotated object is a dictionary and, if it is,
            all keys and values are of the types `key_type` and `value_type` respectively.
        """

        def validator(d: Any) -> bool:
            return isinstance(d, dict) and all(
                isinstance(key, key_type) and isinstance(value, value_type)
                for key, value in d.items()
            )

        return Is[validator]
