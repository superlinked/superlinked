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

import pkgutil
from importlib import import_module

import structlog
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry

logger = structlog.getLogger(__name__)


class RegistryLoader:
    @staticmethod
    def get_registry(app_module_path: str) -> SuperlinkedRegistry | None:
        superlinked_registry = None
        try:
            package = import_module(app_module_path)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if not is_pkg:
                    try:
                        module = import_module(module_name)
                        if hasattr(module, "SuperlinkedRegistry"):
                            superlinked_registry = module.SuperlinkedRegistry
                    except AttributeError:
                        logger.exception("superlinked registry was not found in module", module_name=module_name)
                    except Exception:  # pylint: disable=broad-except
                        logger.exception("error while loading SuperlinkedRegistry from module", module_name=module_name)
        except ImportError:
            logger.exception("not found the package at the specified path", app_module_path=app_module_path)
        except Exception:  # pylint: disable=broad-except
            logger.exception("error occurred while loading the package", app_module_path=app_module_path)
        return superlinked_registry
