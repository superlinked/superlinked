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
import logging
import os

from superlinked.framework.storage.in_memory.object_serializer import ObjectSerializer

from executor.app.service.file_handler_service import FileHandlerService

logger = logging.getLogger(__name__)


EMPTY_JSON_OBJECT_SIZE = 4  # 4 characters: "{}"


class FileObjectSerializer(ObjectSerializer):
    def __init__(self, file_handler_service: FileHandlerService) -> None:
        super().__init__()
        self.__file_handler_service = file_handler_service

    def write(self, serialized_object: str, key: str) -> None:
        self.__file_handler_service.ensure_folder()

        logger.info("Persisting database with id: %s", key)
        file_with_path = self.__file_handler_service.generate_filename(key)
        with open(file_with_path, "w", encoding="utf-8") as file:
            logger.info("Writing id: %s to file: %s", key, file_with_path)
            json.dump(serialized_object, file)

    def read(self, key: str) -> str:
        logger.info("Restoring database using id: %s", key)
        file_with_path = self.__file_handler_service.generate_filename(key)

        result = "{}"
        try:
            if os.path.isfile(file_with_path):
                with open(file_with_path, encoding="utf-8") as file:
                    if os.stat(file_with_path).st_size >= EMPTY_JSON_OBJECT_SIZE:
                        result = json.load(file)
                        logger.info("Database successfully restored from file: %s", file_with_path)
            else:
                logger.info("No file available for database restoration at path: %s", file_with_path)
        except json.JSONDecodeError:
            logger.exception("File is present but contains invalid data. File: %s", file_with_path)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("An error occurred during the file read operation. File: %s", file_with_path)
        return result
