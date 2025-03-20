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

"""
In this file we are ignoring a transformers warning, because in batch we set this env var
and even though it is labelled as deprecated, they still use the old one in some places.
"""

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message=(
            "Using `TRANSFORMERS_CACHE` is deprecated and "
            "will be removed in v5 of Transformers. Use `HF_HOME` instead."
        ),
    )
    from sentence_transformers import SentenceTransformer

__all__ = ["SentenceTransformer"]
