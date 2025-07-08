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

from importlib.metadata import version

import structlog

logger = structlog.getLogger(__name__)


class VersionResolver:
    @staticmethod
    def get_version_for_package(package_name: str) -> str | None:
        try:
            return version(package_name)
        except (ImportError, ValueError) as e:
            logger.warning(
                "failed to get version for package",
                package_name=package_name,
                error_detail=str(e),
                error_type=type(e).__name__,
            )
        return None
