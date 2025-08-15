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

import structlog
from beartype.typing import Sequence

from superlinked.framework.common.exception import InvalidInputException

logger = structlog.getLogger()


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
        base_module_name: str,
        recursive: bool = False,
        depth: int = 0,
        ignore_missing_modules: Sequence[str] | None = None,
    ) -> ModuleType:
        if depth > ClassHelper.MAX_MODULE_DEPTH:
            raise InvalidInputException(f"Module import depth limit ({ClassHelper.MAX_MODULE_DEPTH}) exceeded.")
        base_module: ModuleType = ClassHelper._import_module(base_module_name)
        if recursive and hasattr(base_module, "__path__"):
            for _, modname, is_pkg in pkgutil.walk_packages(base_module.__path__):
                module_name = f"{base_module.__name__}.{modname}"
                if not is_pkg:
                    try:
                        ClassHelper._import_module(module_name)
                    except ModuleNotFoundError as e:
                        if ignore_missing_modules and e.name in ignore_missing_modules:
                            logger.warning(
                                "module not found error ignored",
                                module_name=module_name,
                                missing_module=e.name,
                                ignore_missing_modules=ignore_missing_modules,
                            )
                            continue
                        raise
                else:
                    ClassHelper.import_module(module_name, recursive, depth + 1, ignore_missing_modules)
        return base_module

    @staticmethod
    def _import_module(module_name: str) -> ModuleType:
        if module_name not in sys.modules:
            module: ModuleType = importlib.import_module(module_name)
            logger.debug("module imported", module_name=module_name)
            sys.modules[module_name] = module
        return sys.modules[module_name]
