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
from pathlib import Path

import jsonschema
from beartype.typing import Any, Sequence

from superlinked.framework.common.exception import ValidationException


class JsonSchemaValidator:
    def __init__(self, base_dir: Path, schema_ids: Sequence[str] | None = None) -> None:
        self._base_dir = base_dir
        self._schemas = dict[str, dict[str, Any]]()
        for schema_id in schema_ids or []:
            self._load_schema(schema_id)

    def _load_schema(self, schema_id: str) -> None:
        with (self._base_dir / f"{schema_id}.json").open(
            mode="r", encoding="utf-8"
        ) as schema:
            self._schemas[schema_id] = json.load(schema)

    def validate(self, message: dict[str, Any], schema_id: str) -> None:
        if schema := self._schemas.get(schema_id):
            jsonschema.validate(message, schema)
        else:
            raise ValidationException(
                f"The json schema descriptor cannot be found with the given id {schema_id}"
            )
