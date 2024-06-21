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

from abc import ABC, abstractmethod


class ObjectSerializer(ABC):
    """
    This abstract base class outlines the interface for an object serializer.
    """

    @abstractmethod
    def read(self, field_identifier: str, app_identifier: str) -> str:
        """
        The identifier represents the field name.
        The method should return the object that corresponds to the field, that the writer previously written.
        The app_identifier is a unique deterministic id specific to each application and its version.
        """

    @abstractmethod
    def write(
        self, field_identifier: str, serialized_object: str, app_identifier: str
    ) -> None:
        """
        The object to be written is a dictionary.
        The identifier represents a field name and the value is the string
        representation of a dict, serialized using JSON.
        The app_identifier is a unique deterministic id specific to each application and its version.
        """
