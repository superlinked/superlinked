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

import json
import os

import structlog
from superlinked.framework.storage.in_memory.object_serializer import ObjectSerializer

from executor.app.service.file_handler_service import FileHandlerService

logger = structlog.getLogger(__name__)


EMPTY_JSON_OBJECT_SIZE = 4  # 4 characters: "{}"


class FileObjectSerializer(ObjectSerializer):
    def __init__(self, file_handler_service: FileHandlerService) -> None:
        super().__init__()
        self.__file_handler_service = file_handler_service

    def write(self, serialized_object: str, key: str) -> None:
        self.__file_handler_service.ensure_folder()

        logger.info("persist database", id=key)
        file_with_path = self.__file_handler_service.generate_filename(key)
        with open(file_with_path, "w", encoding="utf-8") as file:
            logger.info("write file", id=key, path=file_with_path)
            json.dump(serialized_object, file)

    def read(self, key: str) -> str:
        file_with_path = self.__file_handler_service.generate_filename(key)

        result = "{}"
        try:
            if os.path.isfile(file_with_path):
                with open(file_with_path, encoding="utf-8") as file:
                    if os.stat(file_with_path).st_size >= EMPTY_JSON_OBJECT_SIZE:
                        result = json.load(file)
                        logger.info("restored database", id=key, path=file_with_path)
            else:
                logger.info("no file available", path=file_with_path)
        except json.JSONDecodeError:
            logger.exception("invalid data found in file", path=file_with_path)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("error occurred during file read operation", path=file_with_path)
        return result
