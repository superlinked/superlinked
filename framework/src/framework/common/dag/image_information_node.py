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
from typing_extensions import override

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import ImageData
from superlinked.framework.common.schema.blob_information import BlobInformation


class ImageInformationNode(Node[ImageData]):
    def __init__(
        self,
        image_blob_node: Node[BlobInformation],
        description_node: Node[str],
    ) -> None:
        nodes: list[Node] = [image_blob_node]
        if description_node is not None:
            nodes.append(description_node)
        super().__init__(ImageData, nodes)
        self.image_node_id = image_blob_node.node_id
        self.description_node_id = description_node.node_id

    @override
    def _get_node_id_parameters(self) -> dict[str, Any]:
        return {}
