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

import os

# TODO: https://linear.app/superlinked/issue/FAI-1786/create-settings-mechanics-for-congig
MAX_DAG_DEPTH = 20
DEFAULT_WEIGHT = 1.0
DEFAULT_NOT_AFFECTING_WEIGHT = 0.0
DEFAULT_LIMIT = -1
ONLINE_PUT_CHUNK_SIZE: int = int(os.getenv("ONLINE_PUT_CHUNK_SIZE", "6000"))
