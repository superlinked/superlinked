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


import inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from starlette import status

<<<<<<< HEAD
=======
from executor.app.exception.exception import (
    DataLoaderAlreadyRunningException,
    DataLoaderNotFoundException,
    DataLoaderTaskNotFoundException,
)
>>>>>>> 6749add (server/1.12.0)
from executor.app.service.data_loader import DataLoader
from executor.app.service.supervisor_service import SupervisorService

router = APIRouter()


class LoadDataPayload(BaseModel):
    run_in_background: bool = False


@cbv(router)
class ManagementRouter:
    __supervisor_service: SupervisorService = Depends(lambda: inject.instance(SupervisorService))
    __data_loader: DataLoader = Depends(lambda: inject.instance(DataLoader))

    @router.get(
        "/health",
        summary="Returns with 200 OK, if the application is healthy",
        status_code=status.HTTP_200_OK,
    )
    async def health_check(self) -> JSONResponse:
        return JSONResponse(content={"message": "OK"}, status_code=status.HTTP_200_OK)

    @router.post(
        "/reload",
        summary="Returns with 200 and the result of the reload",
        status_code=status.HTTP_200_OK,
    )
    async def reload(self) -> JSONResponse:
        restart_result = self.__supervisor_service.restart()  # pylint: disable=no-member
        return JSONResponse(content={"result": restart_result}, status_code=status.HTTP_200_OK)

    @router.post(
<<<<<<< HEAD
        "/data-loader/run",
        summary=(
            "Returns with 202 ACCEPTED if the data loader successfully started "
            "in the background, or 200 OK if the data was loaded immediately"
        ),
        status_code=status.HTTP_200_OK,
    )
    async def load_data(self) -> JSONResponse:
        task_ids = self.__data_loader.load()  # pylint: disable=no-member
        if task_ids:
            return JSONResponse(
                content={
                    "result": (
                        "Background task(s) successfully started. For status, check: `/data-loader/<task_id>/status`"
                    ),
                    "task_ids": list(task_ids),
                },
                status_code=status.HTTP_202_ACCEPTED,
            )
        return JSONResponse(
            content={"result": "Data load initiation failed, no sources available for execution"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @router.get(
        "/data-loader/{task_id}/status",
        summary=(
            "Returns the status of a specific data loader task by its id. "
            "200 OK with result if exists, otherwise 404."
        ),
        status_code=status.HTTP_200_OK,
    )
    async def get_data_loader_status(self, task_id: str) -> JSONResponse:
        task_status = self.__data_loader.get_task_status_by_name(task_id)  # pylint: disable=no-member
        if task_status:
            return JSONResponse(content={"result": task_status}, status_code=status.HTTP_200_OK)
        return JSONResponse(
            content={"result": f"Task not found with id: {task_id}"}, status_code=status.HTTP_404_NOT_FOUND
=======
        "/data-loader/{name}/run",
        summary=(
            "Returns with 202 ACCEPTED if the data loader found and started in the background. "
            "If the data loader is not found by the given name, 404 NOT FOUND."
        ),
        status_code=status.HTTP_200_OK,
    )
    async def load_data(self, name: str) -> JSONResponse:
        try:
            self.__data_loader.load(name)  # pylint: disable=no-member
            return JSONResponse(
                content={"result": f"Background task successfully started with name: {name}"},
                status_code=status.HTTP_202_ACCEPTED,
            )
        except DataLoaderNotFoundException:
            return JSONResponse(
                content={"result": f"Data load initiation failed, no source found with name: {name}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except DataLoaderAlreadyRunningException:
            return JSONResponse(
                content={"result": f"Data load already running with name: {name}"},
                status_code=status.HTTP_409_CONFLICT,
            )

    @router.get(
        "/data-loader/{name}/status",
        summary=(
            "Returns the status of a specific data loader task by its name. "
            "200 OK with result if exists, otherwise 404 NOT FOUND."
        ),
        status_code=status.HTTP_200_OK,
    )
    async def get_data_loader_status(self, name: str) -> JSONResponse:
        try:
            task_status = self.__data_loader.get_task_status_by_name(name)  # pylint: disable=no-member
            return JSONResponse(content={"result": task_status}, status_code=status.HTTP_200_OK)
        except DataLoaderTaskNotFoundException:
            return JSONResponse(
                content={"result": f"Task not found with name: {name}"}, status_code=status.HTTP_404_NOT_FOUND
            )

    @router.get(
        "/data-loader/",
        summary="Returns 200 OK with the name and config of your data loaders",
        status_code=status.HTTP_200_OK,
    )
    async def get_data_loaders(self) -> JSONResponse:
        loaders = self.__data_loader.get_data_loaders()  # pylint: disable=no-member
        return JSONResponse(
            content={"result": {name: str(config) for name, config in loaders.items()}}, status_code=status.HTTP_200_OK
>>>>>>> 6749add (server/1.12.0)
        )
