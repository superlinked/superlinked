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

from beartype.typing import Any

from superlinked.framework.common.precision import Precision
from superlinked.framework.dsl.storage.vector_database import VectorDatabase
from superlinked.framework.storage.common.vdb_settings import VDBSettings
from superlinked.framework.storage.mongo_db.mongo_db_connection_params import (
    MongoDBConnectionParams,
)
from superlinked.framework.storage.mongo_db.mongo_db_vdb_connector import (
    MongoDBVDBConnector,
)
from superlinked.framework.storage.mongo_db.search_index.mongo_db_admin_params import (
    MongoDBAdminParams,
)


class MongoDBVectorDatabase(VectorDatabase[MongoDBVDBConnector]):
    """
    MongoDB implementation of the VectorDatabase.

    This class provides a MongoDB-based vector database connector.
    """

    def __init__(  # pylint: disable=R0913
        self,
        host: str,
        db_name: str,
        cluster_name: str,
        project_id: str,
        admin_api_user: str,
        admin_api_password: str,
        default_query_limit: int = 10,
        vector_precision: Precision = Precision.FLOAT16,
        **extra_params: Any
    ) -> None:
        """
        Initialize the MongoDBVectorDatabase.

        Args:
            host (str): The hostname of the MongoDB server.
            db_name (str): The name of the database.
            cluster_name (str): The name of the MongoDB cluster.
            project_id (str): The project ID for MongoDB.
            admin_api_user (str): The admin API username.
            admin_api_password (str): The admin API password.
            default_query_limit (int): Default vector search limit,
                MongoDB does not have a default for it so setting it to a reasonable number of 10.
            vector_precision (Precision): Precision to use for storing vectors. Defaults to FLOAT16.
            **extra_params (Any): Additional parameters for the MongoDB connection.
        """
        super().__init__()
        self._connection_params = MongoDBConnectionParams(
            host,
            db_name,
            MongoDBAdminParams(cluster_name, project_id, admin_api_user, admin_api_password),
            **extra_params
        )
        self._settings = VDBSettings(default_query_limit, vector_precision=vector_precision)

    @property
    def _vdb_connector(self) -> MongoDBVDBConnector:
        """
        Get the MongoDB vector database connector.

        Returns:
            MongoVDBConnector: The MongoDB vector database connector instance.
        """
        return MongoDBVDBConnector(self._connection_params, self._settings)
