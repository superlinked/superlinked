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

import logging

from superlinked.framework.common.logging import PACKAGE_NAME, LoggerConfigurator
from superlinked.framework.common.settings import Settings

LoggerConfigurator.configure_default_logger()
if superlinked_log_level := Settings().SUPERLINKED_LOG_LEVEL:
    logging.getLogger(PACKAGE_NAME).setLevel(superlinked_log_level)
