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


from beartype.typing import Any, Sequence

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.storage_manager.storage_manager import StorageManager
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.executor.query.query_executor import QueryExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.query import QueryObj
from superlinked.framework.dsl.query.query_vector_factory import QueryVectorFactory
from superlinked.framework.dsl.query.result import Result


@TypeValidator.wrap
class QueryMixin:
    """
    A mixin class that provides query execution capabilities for classes that include it.
    This class sets up the necessary infrastructure to execute queries on a set of indices
    using a storage manager.
    """

    def setup_query_execution(
        self, indices: Sequence[Index], storage_manager: StorageManager
    ) -> None:
        """
        Set up the query execution environment by initializing a mapping between indices
        and their corresponding QueryVectorFactory instances.

        Args:
            indices (Sequence[Index]): A sequence of Index instances to be used for query execution.
            storage_manager (StorageManager): The storage manager instance to be used.
        """
        self._query_vector_factory_by_index = {
            index: QueryVectorFactory(
                index._dag, set(index._space_schemas), storage_manager
            )
            for index in indices
        }

    def query(self, query_obj: QueryObj, **params: Any) -> Result:
        """
        Execute a query using the provided QueryObj and additional parameters.

        Args:
            query_obj (QueryObj): The query object containing the query details.
            **params (Any): Additional parameters for the query execution.

        Returns:
            Result: The result of the query execution.

        Raises:
            QueryException: If the query index is not found among the executor's indices.
        """
        if query_vector_factory := self._query_vector_factory_by_index.get(
            query_obj.index
        ):
            # 'self' is an App instance; MyPy can't infer the inheriting class. See [FAI-2085].
            return QueryExecutor(self, query_obj, query_vector_factory).query(**params)  # type: ignore

        raise QueryException(
            (
                f"Query index {query_obj.index} is not amongst the executor's indices: ",
                f" {list(self._query_vector_factory_by_index.keys())}",
            )
        )
