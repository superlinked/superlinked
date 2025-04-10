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

import atexit
import inspect
import json
import os
import time
from collections import defaultdict
from functools import wraps
from threading import Lock, Thread

from asgi_correlation_id.context import correlation_id
from beartype.typing import Any, Callable
from typing_extensions import override

from superlinked.framework.common.settings import Settings


class ExecutionTimer:
    _instances: dict[str, "ExecutionTimer"] = {}

    def __new__(cls, output_path: str) -> "ExecutionTimer":
        if output_path not in cls._instances:
            cls._instances[output_path] = super().__new__(cls)
            instance = cls._instances[output_path]
            object.__setattr__(instance, "_initialized", False)
        return cls._instances[output_path]

    def __init__(self, output_path: str) -> None:
        if not self.__dict__.get("_initialized", False):
            self.output_path = output_path
            self.lock = Lock()
            self._data: dict[str, dict[str, list[dict[str, float | None]]]] = defaultdict(
                lambda: defaultdict(list)
            )  # In-memory data store
            dir_path = os.path.dirname(output_path) or "."
            os.makedirs(dir_path, exist_ok=True)
            self._flush_interval = Settings().SUPERLINKED_EXECUTION_TIMER_INTERVAL_MS
            self._flush_thread = Thread(target=self._flush_periodically, daemon=True)
            self._flush_thread.start()
            self.__dict__["_initialized"] = True
            atexit.register(self.flush)

    def start(self, function_id: str) -> None:
        process_id = self._get_process_id()
        current_time = time.time() * 1000
        with self.lock:
            self._data[process_id][function_id].append({"start": current_time, "end": None})

    def stop(self, function_id: str) -> None:
        process_id = self._get_process_id()
        current_time = time.time() * 1000
        with self.lock:
            records = self._data[process_id][function_id]
            if not records:
                return

            last_record = records[-1]
            if last_record["end"] is None:
                last_record["end"] = current_time
                self._update_statistics(records)

    @classmethod
    def flush(cls) -> None:
        """Flush the in-memory data to the output file immediately for all ExecutionTimer instances."""
        for instance in cls._instances.values():
            if hasattr(instance, "lock"):
                with instance.lock:
                    existing_data = instance._read_from_file()
                    merged_data = instance._merge_data(existing_data, instance._data)
                    instance._write_to_file(merged_data)
                    instance._data = defaultdict(lambda: defaultdict(list))  # Reset in-memory data

    def _flush_periodically(self) -> None:
        while True:
            time.sleep(self._flush_interval)
            self.flush()

    def _update_statistics(self, records: list[dict]) -> None:
        completed_records = [r for r in records if r["end"] is not None]
        n_times = len(completed_records)
        if n_times == 0:
            return

        total_time = sum(r["end"] - r["start"] for r in completed_records)
        avg_time = total_time / n_times

        records[-1].update({"cumulative": total_time, "average": avg_time, "n_times": n_times})

    def _read_from_file(self) -> dict:
        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_to_file(self, data: dict) -> None:
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _merge_data(self, existing_data: dict, new_data: dict) -> dict:
        for process_id, functions in new_data.items():
            if process_id not in existing_data:
                existing_data[process_id] = {}
            for function_id, records in functions.items():
                if function_id not in existing_data[process_id]:
                    existing_data[process_id][function_id] = []
                existing_data[process_id][function_id].extend(records)
        return existing_data

    def _get_process_id(self) -> str:
        return correlation_id.get() or "not_in_a_request"


class ExecutionTimeEvaluator:
    def __init__(self, input_path: str) -> None:
        self.input_path = input_path
        self.execution_times = self._read_from_file()

    def _read_from_file(self) -> dict:
        try:
            with open(self.input_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def aggregate_times(self, aggregation_type: str = "cumulative") -> tuple[dict[str, float], dict[str, float]]:
        aggregated_by_process: dict[str, float] = defaultdict(float)
        aggregated_by_function: dict[str, float] = defaultdict(float)

        for process_id, functions in self.execution_times.items():
            for function_id, records in functions.items():
                completed_records = [r for r in records if r["end"] is not None]
                total_time = sum(r["end"] - r["start"] for r in completed_records)

                if aggregation_type == "average" and completed_records:
                    total_time /= len(completed_records)

                aggregated_by_process[process_id] += total_time
                aggregated_by_function[function_id] += total_time

        return dict(aggregated_by_process), dict(aggregated_by_function)

    def plot_execution_times(self, function_name: str | None = None) -> None:
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

        avg_times: list[float] = []
        cumulative_times: list[float] = []

        for functions in self.execution_times.values():
            for function_id, records in functions.items():
                if function_name is None or function_id == function_name:
                    avg_times.extend(r["average"] for r in records if "average" in r)
                    cumulative_times.extend(r["cumulative"] for r in records if "cumulative" in r)

        if avg_times:
            x_range = range(len(avg_times))
            plt.plot(x_range, avg_times, label="Average time", alpha=0.7, marker="o")
            plt.plot(x_range, cumulative_times, label="Cumulative time", alpha=0.7, marker="x")

            plt.xlabel("Nth Execution Instance")
            plt.ylabel("Execution Time (ms)")
            plt.title("Execution Time Over Time for All Inputs")
            plt.xticks(x_range)
            plt.legend()
            plt.show()


class NullExecutionTimer(ExecutionTimer):
    """Does nothing"""

    def __init__(self, output_path: str) -> None:  # pylint: disable=super-init-not-called
        pass

    @override
    def start(self, function_id: str) -> None:
        pass

    @override
    def stop(self, function_id: str) -> None:
        pass

    @override
    @classmethod
    def flush(cls) -> None:
        pass


def getTimer() -> ExecutionTimer:  # pylint: disable=invalid-name
    """Get or create an ExecutionTimer instance for the given output path.

    Args:
        output_path: Path to the JSON file where timing data will be stored

    Returns:
        The ExecutionTimer instance for the given output path
    """
    settings = Settings()
    if not settings.ENABLE_PROFILING:
        return NullExecutionTimer("None")
    output_path: str | None = settings.SUPERLINKED_EXECUTION_TIMER_FILE_PATH
    if not output_path:
        raise ValueError(
            "SUPERLINKED_EXECUTION_TIMER_FILE_PATH must be specified when ENABLE_PROFILING is True. "
            "Please set this environment variable to a valid file path where timing data json will be stored."
        )
    return ExecutionTimer(output_path)


def time_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not Settings().ENABLE_PROFILING:
            return func(*args, **kwargs)

        timer = getTimer()
        if args and hasattr(args[0], "__class__"):
            prefix = args[0].__class__.__name__
            function_id = f"{prefix}_{func.__name__}"
        else:
            function_id = func.__name__
        timer.start(function_id)
        try:
            return func(*args, **kwargs)
        finally:
            timer.stop(function_id)

    return wrapper


def time_execution_with_arg(arg_name: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            timer = getTimer()
            if not Settings().ENABLE_PROFILING:
                return func(*args, **kwargs)

            if args and hasattr(args[0], "__class__"):
                prefix = args[0].__class__.__name__
                function_id = f"{prefix}_{func.__name__}"
            else:
                function_id = func.__name__

            if arg_name in kwargs:
                function_id = f"{function_id}_{str(kwargs[arg_name])}"
            elif len(args) > 1:  # Skip self/cls argument
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if arg_name in params:
                    arg_pos = params.index(arg_name)
                    if arg_pos < len(args):
                        function_id = f"{function_id}_{str(args[arg_pos])}"

            timer.start(function_id)
            try:
                return func(*args, **kwargs)
            finally:
                timer.stop(function_id)

        return wrapper

    return decorator
