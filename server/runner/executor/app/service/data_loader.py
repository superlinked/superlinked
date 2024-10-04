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

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

import pandas as pd
import structlog
from pandas.io.json._json import JsonReader
from pandas.io.parsers import TextFileReader
from pydantic.alias_generators import to_snake
from superlinked.framework.dsl.source.data_loader_source import DataFormat, DataLoaderConfig, DataLoaderSource

from executor.app.configuration.app_config import AppConfig
from executor.app.exception.exception import DataLoaderNotFoundException

logger = structlog.getLogger(__name__)


class DataLoader:
    def __init__(self, app_config: AppConfig) -> None:
        self._app_config = app_config
        self._data_loader_sources: dict[str, DataLoaderSource] = {}

    def register_data_loader_sources(self, data_loader_sources: Sequence[DataLoaderSource]) -> None:
        for source in data_loader_sources:
            if source.name in self._data_loader_sources:
                logger.warning("skipped registration", reason="already registered", source_name=source.name)
                continue
            self._data_loader_sources[to_snake(source.name)] = source

    def get_data_loaders(self) -> dict[str, DataLoaderConfig]:
        return {name: source.config for name, source in self._data_loader_sources.items()}

    def load(self, name: str) -> None:
        data_loader_source = self._data_loader_sources.get(name)
        if not data_loader_source:
            msg = f"Data loader with name: {name} not found"
            raise DataLoaderNotFoundException(msg)
        task = asyncio.create_task(asyncio.to_thread(self.__read_and_put_data, data_loader_source))
        task.add_done_callback(self._task_done_callback)
        logger.info("started data load", configuration=data_loader_source.config, task_name=task.get_name())

    def __read_and_put_data(self, source: DataLoaderSource) -> None:
        data = self.__read_data(source.config.path, source.config.format, source.config.pandas_read_kwargs)
        if isinstance(data, pd.DataFrame):
            self.__print_memory_usage(data)
            logger.debug("loaded data frame to memory", chunked=False, size=len(data))
            source.put([data])
        elif isinstance(data, TextFileReader | JsonReader):
            for chunk in data:
                self.__print_memory_usage(chunk)
                logger.debug("loaded data frame to memory", chunked=True, size=len(chunk))
                source.put([chunk])
        else:
            error_message = (
                "The returned object from the Pandas read method was not of the "
                f"expected type. Actual type: {type(data)}"
            )
            raise TypeError(error_message)
        logger.info("finished data load", source_name=source.name)

    def _task_done_callback(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("failed task", task_name=task.get_name(), exc_info=e)

    def __read_data(
        self, path: str, data_format: DataFormat, pandas_read_kwargs: dict[str, Any] | None
    ) -> pd.DataFrame | TextFileReader | JsonReader:
        kwargs = pandas_read_kwargs or {}
        match data_format:
            case DataFormat.CSV:
                return pd.read_csv(path, **kwargs)
            case DataFormat.FWF:
                return pd.read_fwf(path, **kwargs)
            case DataFormat.XML:
                return pd.read_xml(path, **kwargs)
            case DataFormat.JSON:
                return pd.read_json(path, **kwargs)
            case DataFormat.PARQUET:
                return pd.read_parquet(path, **kwargs)
            case DataFormat.ORC:
                return pd.read_orc(path, **kwargs)
            case _:
                msg = "Unsupported data format: %s"
                raise ValueError(msg, data_format)

    # TODO: This is printing not logging the data. See FAI-2328
    def __print_memory_usage(self, df: pd.DataFrame) -> None:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            df.info(memory_usage=True)
