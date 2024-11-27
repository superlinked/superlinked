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

import datetime


def now() -> int:
    dt = datetime.datetime.now(datetime.timezone.utc)
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())


def convert_datetime_to_utc_timestamp(datetime_object: datetime.datetime) -> int:
    return int(datetime_object.replace(tzinfo=datetime.timezone.utc).timestamp())


def convert_utc_timestamp_to_datetime(utc_timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(utc_timestamp, tz=datetime.timezone.utc)
