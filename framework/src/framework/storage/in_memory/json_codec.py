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

import numpy as np
from beartype.typing import Any

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.schema.blob_information import BlobInformation


class JsonEncoder(json.JSONEncoder):
    def default(self, o: object) -> dict[str, str | list]:
        object_ = o  # `o` cannot be renamed because it would break the JsonEncoder.default's interface
        if isinstance(object_, Vector):
            return {"type": "__Vector__", "value": object_.value.tolist()}
        if isinstance(object_, BlobInformation):
            return {"type": "__BlobInformation__", "value": object_.path or ""}
        return super().default(object_)


class JsonDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(object_hook=self.decode_dict, *args, **kwargs)

    def decode_dict(
        self, dict_: dict[str, Any]
    ) -> Vector | BlobInformation | dict[str, Any]:
        if "type" in dict_:
            if dict_["type"] == "__Vector__":
                return Vector(np.array(dict_["value"]))
            if dict_["type"] == "__BlobInformation__":
                return BlobInformation(path=dict_["value"])
        return dict_
