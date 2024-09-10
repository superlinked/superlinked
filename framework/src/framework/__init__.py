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

from superlinked.framework.common.superlinked_logging import (
    SuperlinkedLoggerConfigurator,
)

__version__ = "0.0.0"  # This will be updated by semantic-release

SuperlinkedLoggerConfigurator.configure_default_logger()


def get_version() -> str:
    return __version__
