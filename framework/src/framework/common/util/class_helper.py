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

import importlib
import inspect
import pkgutil
import sys
from types import ModuleType

from beartype.typing import TypeVar

from superlinked.framework.common.exception import RecursionException

BaseClassT = TypeVar("BaseClassT")


class ClassHelper:
    MAX_MODULE_DEPTH = 20

    @staticmethod
    def get_class(base_module_name: str, class_name: str) -> type | None:
        base_module = ClassHelper.import_module(base_module_name, recursive=True)
        for name, obj in inspect.getmembers(base_module, inspect.isclass):
            if name == class_name:
                return obj
        return None

    @staticmethod
    def import_module(
        base_module_name: str, recursive: bool = False, depth: int = 0
    ) -> ModuleType:
        if depth > ClassHelper.MAX_MODULE_DEPTH:
            raise RecursionException(
                f"Module import depth limit ({ClassHelper.MAX_MODULE_DEPTH}) exceeded."
            )
        base_module: ModuleType = ClassHelper._import_module(base_module_name)
        if recursive and hasattr(base_module, "__path__"):
            for _, modname, is_pkg in pkgutil.walk_packages(base_module.__path__):
                module_name = f"{base_module.__name__}.{modname}"
                if not is_pkg:
                    ClassHelper._import_module(module_name)
                else:
                    ClassHelper.import_module(module_name, recursive, depth + 1)
        return base_module

    @staticmethod
    def _import_module(module_name: str) -> ModuleType:
        if module_name not in sys.modules:
            module: ModuleType = importlib.import_module(module_name)
            sys.modules[module_name] = module
        return sys.modules[module_name]
