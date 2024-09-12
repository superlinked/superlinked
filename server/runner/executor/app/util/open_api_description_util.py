import json
import os
from typing import Any

import structlog

logger = structlog.getLogger(__name__)


class OpenApiDescriptionUtil:
    @staticmethod
    def get_open_api_description_by_key(key: str, file_path: str | None = None) -> dict[str, Any]:
        if file_path is None:
            file_path = os.path.join(os.getcwd(), "executor/openapi/static_endpoint_descriptor.json")
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
            open_api_description = data.get(key)
            if open_api_description is None:
                logger.warning("no OpenAPI description was found for the provided key", key=key)
            return open_api_description
