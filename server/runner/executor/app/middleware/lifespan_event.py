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

# Temporary ignore due to vdb connector access. Fix in: FAI-1961
# ruff: noqa: SLF001

from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager

import inject
import structlog
from fastapi import FastAPI, status
from superlinked.framework.dsl.app.rest.rest_app import RestApp
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

from executor.app.configuration.app_config import AppConfig
from executor.app.service.data_loader import DataLoader
from executor.app.service.persistence_service import PersistenceService
from executor.app.util.fast_api_handler import FastApiHandler
from executor.app.util.open_api_description_util import OpenApiDescriptionUtil
from executor.app.util.registry_loader import RegistryLoader

logger = structlog.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_application(app)
    yield
    teardown_application(app)


def setup_application(app: FastAPI) -> None:
    persistence_service: PersistenceService = inject.instance(PersistenceService)
    data_loader: DataLoader = inject.instance(DataLoader)
    app_config: AppConfig = inject.instance(AppConfig)

    if registry := RegistryLoader.get_registry(app_config.APP_MODULE_PATH):
        rest_executors = [executor for executor in registry.get_executors() if isinstance(executor, RestExecutor)]
        _setup_executors(app, rest_executors, persistence_service, data_loader, app_config)

    persistence_service.restore()


def teardown_application(_: FastAPI) -> None:
    persistence_service: PersistenceService = inject.instance(PersistenceService)
    logger.info("shutdown event detected")
    persistence_service.persist()


def _setup_executors(
    app: FastAPI,
    rest_executors: Sequence[RestExecutor],
    persistence_service: PersistenceService,
    data_loader: DataLoader,
    app_config: AppConfig,
) -> None:
    for executor in rest_executors:
        _validate_recency_space(executor, app_config)
        _validate_in_memory_with_multiple_workers(executor, app_config)
        try:
            rest_app = executor.run()
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("failed to run executor")
            continue
        data_loader.register_data_loader_sources(rest_app.data_loader_sources)
        persistence_service.register(rest_app.storage_manager._vdb_connector)
        _register_routes(app, rest_app)


def _validate_in_memory_with_multiple_workers(executor: RestExecutor, app_config: AppConfig) -> None:
    if isinstance(executor._vector_database, InMemoryVectorDatabase) and app_config.WORKER_COUNT > 1:
        msg = (
            "In-memory database is not compatible with configurations exceeding a single worker. "
            "Reduce the worker count to one or employ a persistent vector database."
        )
        raise ValueError(msg)


def _validate_recency_space(executor: RestExecutor, app_config: AppConfig) -> None:
    if _has_recency_space(executor._indices) and app_config.DISABLE_RECENCY_SPACE:
        msg = "RecencySpace found in Index but is disabled. Either enable RecencySpace or remove it from the Index."
        raise ValueError(msg)


def _register_routes(app: FastAPI, rest_app: RestApp) -> None:
    fast_api_handler: FastApiHandler = FastApiHandler(rest_app.handler)
    for path in rest_app.handler.ingest_paths:
        app.add_api_route(
            path=path,
            endpoint=fast_api_handler.ingest,
            methods=["POST"],
            status_code=status.HTTP_202_ACCEPTED,
            openapi_extra=OpenApiDescriptionUtil.get_open_api_description_by_key("ingest"),
        )
        logger.info("registered ingest endpoint", path=path, method="POST")
    for path in rest_app.handler.query_paths:
        app.add_api_route(
            path=path,
            endpoint=fast_api_handler.query,
            methods=["POST"],
            openapi_extra=OpenApiDescriptionUtil.get_open_api_description_by_key("query"),
        )
        logger.info("registered query endpoint", path=path, method="POST")


def _has_recency_space(indices: Sequence[Index]) -> bool:
    return any(
        isinstance(space, RecencySpace) for index in indices if hasattr(index, "__spaces") for space in index.__spaces
    )
