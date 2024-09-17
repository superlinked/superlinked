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


from functools import partial

import structlog
from beartype.typing import Any, Sequence

from superlinked.framework.common.dag.context import (
    CONTEXT_COMMON,
    CONTEXT_COMMON_NOW,
    ExecutionContext,
    ExecutionEnvironment,
    NowStrategy,
)
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.schema.id_schema_object import IdSchemaObject
from superlinked.framework.common.storage_manager.knn_search_params import (
    KNNSearchParams,
)
from superlinked.framework.common.storage_manager.search_result_item import (
    SearchResultItem,
)
from superlinked.framework.dsl.executor.executor import App
from superlinked.framework.dsl.query.nlq_param_evaluator import NLQParamEvaluator
from superlinked.framework.dsl.query.query import QueryObj
from superlinked.framework.dsl.query.query_filter_information import (
    QueryFilterInformation,
)
from superlinked.framework.dsl.query.query_filters import QueryFilters
from superlinked.framework.dsl.query.query_param_information import (
    QueryParamInformation,
)
from superlinked.framework.dsl.query.query_vector_factory import QueryVectorFactory
from superlinked.framework.dsl.query.result import Result, ResultEntry

logger = structlog.getLogger()


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
        self._logger = logger.bind(
            schema=self.query_obj.schema._schema_name,
            limit=self.query_obj.limit,
            radius=self.query_obj.radius,
        )

    def query(self, **params: Any) -> Result:
        """
        Execute a query with keyword parameters.

        Args:
            **params: Arbitrary arguments with keys corresponding to the `name` attribute of the `Param` instance.

        Returns:
            Result: The result of the query execution that can be inspected and post-processed.

        Raises:
            QueryException: If the query index is not amongst the executor's indices.
        """
        self.__check_executor_has_index()
        query_param_info: QueryParamInformation = self._fill_query_param_info(
            self.query_obj.query_param_info, params
        )
        knn_search_params = self._produce_knn_search_params(
            self.query_obj.query_filter_info, query_param_info
        )
        entities: Sequence[SearchResultItem] = self._knn_search(knn_search_params)
        self._logger.info(
            "executed query",
            n_results=len(entities),
            limit=knn_search_params.limit,
            radius=knn_search_params.radius,
            pii_knn_params=params,
            pii_query_vector=partial(str, knn_search_params.vector),
            pii_natural_query=query_param_info.natural_query,
        )
        return Result(
            self.query_obj.schema,
            self._map_entities_to_result_entries(self.query_obj.schema, entities),
            query_param_info.knn_params,
        )

    def _produce_knn_search_params(
        self,
        query_filter_info: QueryFilterInformation,
        query_param_info: QueryParamInformation,
    ) -> KNNSearchParams:
        limit = query_param_info.limit
        radius = query_param_info.radius
        hard_filters = query_filter_info.get_hard_filters(query_param_info)
        query_vector = self._produce_query_vector(query_filter_info, query_param_info)
        return KNNSearchParams(query_vector, limit, hard_filters, radius)

    def _fill_query_param_info(
        self, query_param_info: QueryParamInformation, params: dict[str, Any]
    ) -> QueryParamInformation:
        query_param_info = query_param_info.alter_with_values(
            params, override_already_set=True
        )
        nlq_params = self._calculate_nlq_params(query_param_info)
        query_param_info = query_param_info.alter_with_values(
            nlq_params, override_already_set=False
        )
        return query_param_info

    def _calculate_nlq_params(
        self,
        query_param_info: QueryParamInformation,
    ) -> dict[str, Any]:
        param_evaluator = NLQParamEvaluator(query_param_info.nlq_param_infos)
        natural_query = query_param_info.natural_query
        client_config = self.query_obj.natural_query_client_config
        nlq_values = param_evaluator.evaluate_param_infos(natural_query, client_config)
        return nlq_values

    def _produce_query_vector(
        self,
        query_filter_info: QueryFilterInformation,
        query_param_info: QueryParamInformation,
    ) -> Vector:
        query_filters = self._get_query_filters(query_filter_info, query_param_info)
        space_weight_map = query_param_info.space_weight_map
        return self.query_vector_factory.produce_vector(
            self.query_obj.index._node_id,
            query_filters,
            space_weight_map,
            self.query_obj.schema,
            self._create_query_context_base(),
        )

    def _get_query_filters(
        self,
        query_filter_info: QueryFilterInformation,
        query_param_info: QueryParamInformation,
    ) -> QueryFilters:
        return QueryFilters(
            query_filter_info.get_looks_like_filter(query_param_info),
            query_filter_info.get_similar_filters(query_param_info),
        )

    def _create_query_context_base(self) -> ExecutionContext:
        eval_context = ExecutionContext(
            environment=ExecutionEnvironment.QUERY,
            data=self.app._context.data,
            now_strategy=NowStrategy.CONTEXT_TIME,
        )
        context_time = self.query_obj._override_now or self.app._context.now()
        eval_context.update_data({CONTEXT_COMMON: {CONTEXT_COMMON_NOW: context_time}})
        return eval_context

    def _knn_search(
        self,
        knn_search_params: KNNSearchParams,
    ) -> Sequence[SearchResultItem]:
        return self.app.storage_manager.knn_search(
            self.query_obj.index._node, self.query_obj.schema, [], knn_search_params
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
        if self.query_obj.index not in self.app._indices:
            raise QueryException(
                f"Query index {self.query_obj.index} is not amongst "
                + f"the executor's indices {self.app._indices}"
            )
