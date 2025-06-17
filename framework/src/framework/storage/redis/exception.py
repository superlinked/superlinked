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


from superlinked.framework.common.const import constants


class RedisTimeoutException(Exception):
    """Exception raised when Redis operations timeout."""

    def __init__(self, message: str | None = None):
        if message is None:
            message = f"Redis timeout ({constants.REDIS_TIMEOUT}ms) exceeded."
        super().__init__(message)


class RedisResultException(Exception):
    """Exception raised when Redis returns incomplete or invalid results."""

    def __init__(self, message: str = "Redis returned incomplete or invalid results"):
        super().__init__(message)
