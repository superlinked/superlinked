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


from beartype.typing import Sequence, cast
from huggingface_hub import InferenceClient
from huggingface_hub.inference._providers import PROVIDER_T
from typing_extensions import override

from superlinked.framework.common.settings import settings
from superlinked.framework.common.space.embedding.model_based.embedding_input import (
    ModelEmbeddingInputT,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine import (
    EmbeddingEngine,
)
from superlinked.framework.common.space.embedding.model_based.engine.embedding_engine_config import (
    EmbeddingEngineConfig,
)

PROVIDER: PROVIDER_T = "hf-inference"
HTTP_PREFIXES = ("http://", "https://")


class HuggingFaceEngine(EmbeddingEngine[EmbeddingEngineConfig]):
    @override
    async def embed(self, inputs: Sequence[ModelEmbeddingInputT], is_query_context: bool) -> list[list[float]]:
        inputs_to_embed = self._validate_and_cast_inputs(inputs)
        client = self._init_inference_client(self._model_name)
        embedding_results = [client.feature_extraction(text=input_) for input_ in inputs_to_embed]
        return cast(list[list[float]], [item for sublist in embedding_results for item in sublist])

    def _validate_and_cast_inputs(self, inputs: Sequence[ModelEmbeddingInputT]) -> Sequence[str]:
        if any(not isinstance(input_, str) for input_ in inputs):
            invalid_type = next(type(input_) for input_ in inputs if not isinstance(input_, str))
            raise ValueError(f"HuggingFaceEngine only supports text inputs, got {invalid_type}")
        return cast(Sequence[str], inputs)

    def _init_inference_client(self, model_name: str) -> InferenceClient:
        token = settings.HUGGING_FACE_API_TOKEN
        if model_name.startswith(HTTP_PREFIXES):
            return InferenceClient(base_url=model_name, token=token, provider=PROVIDER)
        return InferenceClient(model=model_name, token=token, provider=PROVIDER)
