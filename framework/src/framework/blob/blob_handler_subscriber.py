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

import base64

import structlog
from beartype.typing import Sequence, cast

from superlinked.framework.blob.blob_handler import BlobHandler
from superlinked.framework.blob.blob_id_generator import BlobIdGenerator
from superlinked.framework.common.observable import Subscriber
from superlinked.framework.common.parser.parsed_schema import ParsedSchema
from superlinked.framework.common.schema.blob_information import BlobInformation
from superlinked.framework.common.schema.schema_object import Blob

logger = structlog.getLogger()


class BlobHandlerSubscriber(Subscriber[ParsedSchema]):
    def __init__(self, blob_handler: BlobHandler) -> None:
        super().__init__()
        self.__blob_handler = blob_handler

    def update(self, messages: Sequence[ParsedSchema]) -> None:
        for message in messages:
            blob_fields = [field for field in message.fields if isinstance(field.schema_field, Blob)]
            for blob_field in blob_fields:
                object_path = BlobIdGenerator.generate_id_with_path(
                    message.schema._schema_name,
                    message.id_,
                    blob_field.schema_field.name,
                )
                blob_info = cast(BlobInformation, blob_field.value)
                if blob_info.data is None:
                    logger.warning(
                        "Blob data is None, download likely failed.",
                        path=blob_info.path,
                    )
                    continue
                metadata = self.__blob_handler.calculate_metadata(blob_info)

                self.__blob_handler.upload(object_path, base64.b64decode(blob_info.data), metadata)
