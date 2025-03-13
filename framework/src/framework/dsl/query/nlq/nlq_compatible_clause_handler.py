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

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from beartype.typing import cast
from typing_extensions import override

from superlinked.framework.common.interface.evaluated import Evaluated
from superlinked.framework.dsl.query.nlq.param_filler.nlq_annotation import (
    NLQAnnotation,
)
from superlinked.framework.dsl.query.param import ParamInputType
from superlinked.framework.dsl.query.query_clause.query_clause import (
    NLQCompatible,
    QueryClause,
)
from superlinked.framework.dsl.query.typed_param import TypedParam


@dataclass(frozen=True)
class NLQCompatibleClauseHandler(NLQCompatible):
    clause: QueryClause

    def __post_init__(self) -> None:
        if not isinstance(self.clause, NLQCompatible):
            raise ValueError(f"{type(self).__name__} got a non-NLQCompatible clause")

    @property
    def nlq_compatible_clause(self) -> NLQCompatible:
        return cast(NLQCompatible, self.clause)

    @property
    @override
    def is_type_mandatory_in_nlq(self) -> bool:
        # pylint cannot handle interfaces
        return self.nlq_compatible_clause.is_type_mandatory_in_nlq  # pylint: disable=no-member

    @property
    @override
    def nlq_annotations(self) -> list[NLQAnnotation]:
        # pylint cannot handle interfaces
        return self.nlq_compatible_clause.nlq_annotations  # pylint: disable=no-member

    @property
    @override
    def annotation_by_space_annotation(self) -> dict[str, str]:
        # pylint cannot handle interfaces
        return self.nlq_compatible_clause.annotation_by_space_annotation  # pylint: disable=no-member

    @override
    def get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) -> set[ParamInputType | None]:
        # pylint cannot handle interfaces
        return self.nlq_compatible_clause.get_allowed_values(param)  # pylint: disable=no-member

    @classmethod
    def from_clauses(cls, clauses: Sequence[QueryClause]) -> list[NLQCompatibleClauseHandler]:
        return [
            NLQCompatibleClauseHandler(clause.set_defaults_for_nlq())
            for clause in clauses
            if isinstance(clause, NLQCompatible)
        ]
