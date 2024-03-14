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

from superlinked.framework.common.const import DEFAULT_WEIGHT
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.dsl.query.param import FloatParamType, Param
from superlinked.framework.dsl.query.predicate.binary_op import BinaryOp
from superlinked.framework.dsl.query.predicate.query_predicate import QueryPredicate

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["BinaryPredicate"] = False


class BinaryPredicate(QueryPredicate[BinaryOp]):
    def __init__(
        self,
        op: BinaryOp,
        left_param: SchemaField,
        right_param: Param | str | int | float | None,
        weight: FloatParamType = DEFAULT_WEIGHT,
        left_param_node: Node | None = None,
    ) -> None:
        super().__init__(op=op, params=[left_param, right_param], weight_param=weight)
        self.left_param = left_param
        self.right_param = right_param
        self.left_param_node = left_param_node
