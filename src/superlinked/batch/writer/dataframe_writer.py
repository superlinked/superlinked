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

from enum import Enum

from pyspark.sql import DataFrame

from superlinked.batch.dag.exception import InvalidOutputFormat


class Format(Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"


class DataFrameWriter:
    """
    Abstraction around writing spark df output for later processing.

    """

    def __init__(
        self,
        df_name: str | None = None,
        root_path: str = "/batch_results/",
        format: Format = Format.PARQUET,
    ) -> None:
        self.root_path = root_path
        self.df_name = df_name
        self.format = format.value

    def write_data(self, df: DataFrame) -> None:
        output_path = self.root_path + self.df_name if self.df_name else self.root_path
        match self.format:
            case "csv":
                df.write.csv(output_path)
            case "json":
                df.write.json(output_path)
            case "parquet":
                df.write.parquet(output_path)
            case _:
                raise InvalidOutputFormat(
                    f"{self.format} output format is not supported."
                )
