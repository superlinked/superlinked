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
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from superlinked.framework.common.data_types import Vector
from superlinked.framework.storage.field import TextField, VectorField


class ObjectWriter(ABC):
    """
    This abstract base class sets the interface for an object writer. The object to be written is a dictionary.
    The identifier represents a field name and the value is the string representation of a dict, serialized using JSON.
    The app_identifier is a unique deterministic id specific to each application and its version.
    """

    @abstractmethod
    def write(
        self, field_identifier: str, serialized_object: str, app_identifier: str
    ) -> None:
        pass


class ObjectReader(ABC):
    """
    This abstract base class outlines the interface for an object reader. The identifier represents the field name.
    The method should return the object that corresponds to the field, that the writer previously written.
    The app_identifier is a unique deterministic id specific to each application and its version.
    """

    @abstractmethod
    def read(self, field_identifier: str, app_identifier: str) -> str:
        pass


class CustomEncoder(json.JSONEncoder):
    def default(self, o: object) -> dict[str, str | list]:
        if isinstance(o, VectorField):
            return {"type": "__VectorField__", "value": o.value.tolist()}
        if isinstance(o, TextField):
            return {"type": "__TextField__", "value": o.value}
        return super().default(o)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(object_hook=self.decode_dict, *args, **kwargs)

    def decode_dict(
        self, dct: dict[str, Any]
    ) -> VectorField | TextField | dict[str, Any]:
        if "type" in dct:
            if dct["type"] == "__VectorField__":
                return VectorField(Vector(np.array(dct["value"])))
            if dct["type"] == "__TextField__":
                return TextField(dct["value"])
        return dct


class PersistableDict:
    def __init__(self, dict_value: dict) -> None:
        self._dict_identifier: str = self.__class__.__name__
        self._dict: dict[str, Any] = dict_value

    def persist(self, writer: ObjectWriter, app_identifier: str) -> None:
        writer.write(
            self._dict_identifier,
            json.dumps(self._dict, cls=CustomEncoder),
            app_identifier,
        )

    def restore(self, reader: ObjectReader, app_identifier: str) -> None:
        self._dict.update(
            json.loads(
                reader.read(self._dict_identifier, app_identifier), cls=CustomDecoder
            )
        )
