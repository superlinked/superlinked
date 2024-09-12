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

from json import JSONDecodeError

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from superlinked.framework.common.parser.exception import MissingIdException
from superlinked.framework.online.dag.exception import ValueNotProvidedException

from executor.app.configuration.app_config import AppConfig
from executor.app.dependency_register import register_dependencies
from executor.app.exception.exception_handler import (
    handle_bad_request,
    handle_generic_exception,
)
from executor.app.logger import ServerLoggerConfigurator
from executor.app.middleware.lifespan_event import lifespan
from executor.app.middleware.timing_middleware import add_timing_middleware
from executor.app.router.management_router import router as management_router

app_config = AppConfig()

logs_to_suppress = ["sentence_transformers"]
ServerLoggerConfigurator.setup_logger(app_config, logs_to_suppress)

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(ValueNotProvidedException, handle_bad_request)
app.add_exception_handler(MissingIdException, handle_bad_request)
app.add_exception_handler(JSONDecodeError, handle_bad_request)
app.add_exception_handler(Exception, handle_generic_exception)

app.include_router(management_router)

add_timing_middleware(app)
app.add_middleware(CorrelationIdMiddleware)  # This must be the last middleware

register_dependencies()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=None)  # noqa: S104 hardcoded-bind-all-interfaces
