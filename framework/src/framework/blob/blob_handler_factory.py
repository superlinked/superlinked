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

from dataclasses import dataclass

import structlog
from beartype.typing import Any, cast

from superlinked.framework.blob.blob_handler import BlobHandler
from superlinked.framework.common.settings import settings
from superlinked.framework.common.util.class_helper import ClassHelper

logger = structlog.getLogger()


@dataclass(frozen=True)
class BlobHandlerConfig:
    module_path: str
    class_name: str
    class_args: dict[str, Any]


class BlobHandlerFactory:
    @staticmethod
    def create_blob_handler(config: BlobHandlerConfig | None = None) -> BlobHandler | None:
        config = config or BlobHandlerFactory._handle_unset_config()
        if not config:
            return None
        blob_handler_class = ClassHelper.get_class(config.module_path, config.class_name)
        if blob_handler_class is None:
            logger.warning(
                "couldn't find blob implementation",
                module_path=config.module_path,
                class_name=config.class_name,
            )
            return None
        initialized_class = blob_handler_class(**config.class_args)
        logger.info(
            "initialized blob handler",
            module_path=config.module_path,
            class_name=config.class_name,
            class_args=config.class_args,
        )
        return cast(BlobHandler, initialized_class)

    @staticmethod
    def _handle_unset_config() -> None | BlobHandlerConfig:
        module_path = settings.BLOB_HANDLER_MODULE_PATH
        class_name = settings.BLOB_HANDLER_CLASS_NAME
        if module_path is None or class_name is None:
            return None
        config = BlobHandlerConfig(
            module_path=module_path,
            class_name=class_name,
            class_args=settings.BLOB_HANDLER_CLASS_ARGS or {},
        )
        return config
