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

import structlog
from beartype.typing import cast

from superlinked.framework.blob.blob_handler import BlobHandler
from superlinked.framework.common.settings import Settings
from superlinked.framework.common.util.class_helper import ClassHelper

logger = structlog.getLogger()


class BlobHandlerFactory:
    @staticmethod
    def create_blob_handler() -> BlobHandler | None:
        module_path = Settings().BLOB_HANDLER_MODULE_PATH
        class_name = Settings().BLOB_HANDLER_CLASS_NAME
        if module_path is None or class_name is None:
            return None
        blob_handler_class = ClassHelper.get_class(module_path, class_name)
        if blob_handler_class is None:
            logger.warning(
                "couldn't find blob implementation",
                module_path=module_path,
                class_name=class_name,
            )
            return None
        args = Settings().BLOB_HANDLER_CLASS_ARGS or {}
        initialized_class = blob_handler_class(**args)
        logger.info(
            "initialized blob handler",
            module_path=module_path,
            class_name=class_name,
            args=args,
        )
        return cast(BlobHandler, initialized_class)
