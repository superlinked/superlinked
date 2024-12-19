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

from collections.abc import Mapping, Sequence
from itertools import groupby

from beartype.typing import Any, cast
from typing_extensions import TypeVar

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.common.interface.has_annotation import HasAnnotation
from superlinked.framework.common.schema.schema_object import Blob
from superlinked.framework.dsl.query.query_clause import (
    QueryClause,
    SimilarFilterClause,
)

QueryClauseT = TypeVar("QueryClauseT", bound=QueryClause)


class NLQClauseCollector:

    def __init__(self, query_clauses: Sequence[QueryClause]) -> None:
        self._clauses = self._filter_for_nlq_compatible_clauses(query_clauses)
        self._clauses_by_type: Mapping[type[QueryClause], list[QueryClause]] = {
            key: list(group) for key, group in groupby(self._clauses, type)
        }

    @property
    def clauses(self) -> Sequence[QueryClause]:
        return self._clauses

    def get_clauses_by_type(self, clause_type: type[QueryClauseT]) -> Sequence[QueryClauseT]:
        return cast(Sequence[QueryClauseT], self._clauses_by_type.get(clause_type, []))

    @property
    def all_params_have_value_set(self) -> bool:
        return all(isinstance(param, Evaluated) for clause in self._clauses for param in clause.params)

    @classmethod
    def _filter_for_nlq_compatible_clauses(cls, query_clauses: Sequence[QueryClause]) -> list[QueryClause[Any]]:
        def is_nlq_compatible(clause: QueryClause) -> bool:
            if not isinstance(clause, HasAnnotation):
                return False
            if isinstance(clause, SimilarFilterClause):
                fields = clause.field_set.fields
                return not any(isinstance(field, Blob) for field in fields)
            return True

        return [clause for clause in query_clauses if is_nlq_compatible(clause)]
