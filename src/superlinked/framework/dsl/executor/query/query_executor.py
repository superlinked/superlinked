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

from typing import Any

from beartype.typing import Sequence

from superlinked.framework.common.dag.context import (
    CONTEXT_COMMON,
    CONTEXT_COMMON_NOW,
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperation,
)
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.schema.schema_object import SchemaField
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.common.util import time_util
from superlinked.framework.dsl.executor.executor import App
from superlinked.framework.dsl.query.param_evaluator import ParamEvaluator
from superlinked.framework.dsl.query.query import QueryObj
from superlinked.framework.dsl.query.query_filters import QueryFilters
from superlinked.framework.dsl.query.query_vector_factory import QueryVectorFactory
from superlinked.framework.dsl.query.result import Result, ResultEntry
from superlinked.framework.dsl.space.space import Space


class QueryExecutor:
    """
    QueryExecutor provides an interface to execute predefined queries with query time parameters.
    """

    def __init__(
        self,
        app: App,
        query_obj: QueryObj,
        query_vector_factory: QueryVectorFactory,
    ) -> None:
        """
        Initializes the QueryExecutor.

        Args:
            app: An instance of the App class.
            query_obj: An instance of the QueryObj class representing the query to be executed.
            evaluator: An instance of the QueryDagEvaluator class used to evaluate the query.
        """
        self.app = app
        self.query_obj = query_obj
        self.query_vector_factory = query_vector_factory

    def query(self, **params: Any) -> Result:
        """
        Execute a query with keyword parameters.

        Args:
            **params: Arbitrary arguents with keys corresponding to the `name` attribute of the `Param` instance.

        Returns:
            Result: The result of the query execution that can be inspected and post-proceseed.

        Raises:
            QueryException: If the query index is not amongst the executor's indices.
        """
        self.__check_executor_has_index()
        param_evaluator = ParamEvaluator(params)
        limit = param_evaluator.evaluate_limit_param(self.query_obj.limit_)
        radius = param_evaluator.evaluate_radius_param(self.query_obj.radius_)
        hard_filters = param_evaluator.evaluate_hard_filters_param(
            self.query_obj.hard_filters
        )
        entities: Sequence[SearchResultItem] = self._knn(
            self._get_query_vector(param_evaluator), limit, radius, hard_filters
        )
        return Result(
            self.query_obj.schema,
            self._map_entities_to_result_entries(self.query_obj.schema, entities),
        )

    def _get_query_vector(self, param_evaluator: ParamEvaluator) -> Vector:
        query_filters = self._create_query_filters(param_evaluator)
        space_weight_map = self.__get_space_weight_map(param_evaluator)
        return self.query_vector_factory.produce_vector(
            self.query_obj.index._node_id,
            query_filters,
            space_weight_map,
            self.query_obj.schema,
            self._create_query_context_base(),
        )

    def _create_query_filters(self, param_evaluator: ParamEvaluator) -> QueryFilters:
        return QueryFilters(
            self.query_obj.looks_like_filter,
            self.query_obj.similar_filters_by_space,
            param_evaluator,
        )

    def _create_query_context_base(self) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=self.app.executor.context.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        eval_context.update_data(
            {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: self.__query_now()}}
        )
        return eval_context

    def _knn(
        self,
        vector: Vector,
        limit: int | None,
        radius: float | None,
        hard_filters: Sequence[ComparisonOperation[SchemaField]],
    ) -> Sequence[SearchResultItem]:
        return self.app.storage_manager.knn_search(
            self.query_obj.index._node,
            self.query_obj.schema,
            [],
            KNNSearchParams(
                vector=vector,
                limit=limit,
                filters=hard_filters,
                radius=radius,
            ),
        )

    def _map_entities_to_result_entries(
        self, schema: IdSchemaObject, result_items: Sequence[SearchResultItem]
    ) -> Sequence[ResultEntry]:
        return [
            ResultEntry(
                entity,
                self._get_stored_object_or_raise(
                    schema, entity.header.origin_id or entity.header.object_id
                ),
            )
            for entity in result_items
        ]

    def _get_stored_object_or_raise(
        self, schema: IdSchemaObject, object_id: str
    ) -> dict[str, Any]:
        stored_object = self.app.storage_manager.read_object_blob(schema, object_id)
        if not stored_object:
            raise QueryException(
                f"No stored {schema._schema_name} object found for the given object_id: {object_id}"
            )
        return stored_object

    def __check_executor_has_index(self) -> None:
        if self.query_obj.index not in self.app.executor._indices:
            raise QueryException(
                f"Query index {self.query_obj.index} is not amongst "
                + f"the executor's indices {self.app.executor._indices}"
            )

    def __get_space_weight_map(
        self, param_evaluator: ParamEvaluator
    ) -> dict[Space, float]:
        return {
            space: param_evaluator.evaluate_weight_param(weight_obj)
            for space, weight_obj in self.query_obj.builder.space_weight_map.items()
        }

    def __check_now(
        self,
    ) -> int:
        return self.query_obj._override_now or time_util.now()

    def __query_now(self) -> int:
        now_ = self.__check_now()
        if now_ is not None:
            return now_
        raise QueryException(
            (
                f"Environment's '{CONTEXT_COMMON}.{CONTEXT_COMMON_NOW}' ",
                "property should always be initialized for query contexts",
            )
        )
