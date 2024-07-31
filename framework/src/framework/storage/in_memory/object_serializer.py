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
    This abstract base class defines the interface for an object serializer.
    """

    @abstractmethod
    def read(self, key: str) -> str:
        """
        Read the serialized object associated with the given key.
        The method should return the serialized data as a string.
        """

    @abstractmethod
    def write(self, serialized_object: str, key: str) -> None:
        """
        Write the serialized object under the specified key.
        The serialized_object parameter should be a string representation of a serialized dictionary.
        """
