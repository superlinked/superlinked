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

from collections import defaultdict
from dataclasses import dataclass
from itertools import product

from beartype.typing import Mapping, Sequence

from superlinked.framework.common.exception import InvalidInputException
from superlinked.framework.dsl.query.query_clause.query_clause import QueryClause
from superlinked.framework.dsl.space.space import Space


@dataclass(frozen=True)
class SpaceWeightParamInfo:
    global_param_name_by_space: Mapping[Space, str]
    param_names_by_space: Mapping[Space, Sequence[str]]

    @classmethod
    def from_clauses(cls, clauses: Sequence[QueryClause]) -> SpaceWeightParamInfo:
        global_param_name_by_space = SpaceWeightParamInfo.__init_global_param_name_by_space(clauses)
        param_names_by_space = SpaceWeightParamInfo.__init_param_names_by_space(clauses, global_param_name_by_space)
        return SpaceWeightParamInfo(global_param_name_by_space, param_names_by_space)

    @staticmethod
    def __init_global_param_name_by_space(clauses: Sequence[QueryClause]) -> dict[Space, str]:
        global_param_names_by_space = defaultdict[Space, list[str]](list)
        for clause in clauses:
            for space, weight_param_name in clause.get_space_weight_param_name_by_space().items():
                global_param_names_by_space[space].append(weight_param_name)
        if redundant_global_weight_declarations := [
            (space, param_names) for space, param_names in global_param_names_by_space.items() if len(param_names) != 1
        ]:
            space_param_names_str = "\n\t".join(
                [f"{space}: {param_names}" for space, param_names in redundant_global_weight_declarations]
            )
            raise InvalidInputException(
                (
                    "Multiple global space weight parameters found for the same space(s). "
                    f"Each space should have exactly one global weight parameter: {space_param_names_str}"
                )
            )
        return {space: param_names[0] for space, param_names in global_param_names_by_space.items()}

    @staticmethod
    def __init_param_names_by_space(
        clauses: Sequence[QueryClause], global_param_name_by_space: Mapping[Space, str]
    ) -> dict[Space, list[str]]:
        param_names_by_space: defaultdict[Space, list[str]] = defaultdict(list[str])
        none_space_weight_param_names = list[str]()
        for clause in clauses:
            for space, weight_param_name in clause.get_weight_param_name_by_space().items():
                if space is None:
                    none_space_weight_param_names.append(weight_param_name)
                else:
                    param_names_by_space[space].append(weight_param_name)
        parameterized_global_spaces: list[Space] = list(global_param_name_by_space.keys())
        for global_space, weight_param_name in product(parameterized_global_spaces, none_space_weight_param_names):
            param_names_by_space[global_space].append(weight_param_name)
        return dict(param_names_by_space)
