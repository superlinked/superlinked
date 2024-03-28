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

from typing import cast

from superlinked.framework.common.dag.chunking_node import ChunkingNode
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.schema_field_node import SchemaFieldNode
from superlinked.framework.common.dag.text_embedding_node import TextEmbeddingNode
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import InvalidSchemaException
from superlinked.framework.common.schema.schema_object import SchemaObject, String
from superlinked.framework.common.util.type_validator import TypeValidator
from superlinked.framework.dsl.space.space import Space
from superlinked.framework.dsl.space.space_field_set import SpaceFieldSet

TextInput = String | ChunkingNode


class TextSimilaritySpace(Space):
    """
    A text similarity space is used to create vectors from documents in order to search in them
    later on. We only support (SentenceTransformers)[https://www.sbert.net/] models as they have
    finetuned pooling to encode longer text sequences most efficiently.
    """

    def __init__(
        self,
        text: TextInput | list[TextInput],
        model: str,
    ) -> None:
        """
        Initialize the TextSimilaritySpace.

        Args:
            text (TextInput | list[TextInput]): The Text input or a list of Text inputs.
            It is a SchemaFieldObject (String), not a regular python string.
            model (str): The model used for text similarity.
        """
        text_text_node_map = {
            self.__get_root(unchecked_text): self.__generate_embedding_node(
                unchecked_text, model
            )
            for unchecked_text in (text if isinstance(text, list) else [text])
        }
        super().__init__(list(text_text_node_map.keys()), String)
        self.text = SpaceFieldSet(self, set(text_text_node_map.keys()))
        self.__schema_node_map: dict[SchemaObject, TextEmbeddingNode] = {
            schema_field.schema_obj: node
            for schema_field, node in text_text_node_map.items()
        }

    def __get_root(self, text: String | Node) -> String:
        if isinstance(text, String):
            return text
        if isinstance(text, SchemaFieldNode):
            return cast(String, text.schema_field)
        return self.__get_root(text.parents[0])

    def __generate_embedding_node(
        self, text: TextInput, model: str
    ) -> TextEmbeddingNode:
        if isinstance(text, ChunkingNode):
            return TextEmbeddingNode(text, model)
        return TextEmbeddingNode(SchemaFieldNode(text), model)

    def _get_node(self, schema: SchemaObject) -> Node[Vector]:
        if node := self.__schema_node_map.get(schema):
            return node
        raise InvalidSchemaException(
            f"There's no node corresponding to this schema: {schema._schema_name}"
        )

    def _get_all_leaf_nodes(self) -> set[Node[Vector]]:
        return set(self.__schema_node_map.values())


@TypeValidator.wrap
def chunk(
    text: String,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    split_chars_keep: list[str] | None = None,
    split_chars_remove: list[str] | None = None,
) -> ChunkingNode:
    """
    Create smaller chunks from the given text, a String SchemaFieldObject. It is helpful when you search
    for more granular information in your text corpus. It is recommended to try different chunk_sizes to
    find what fits best your use-case. Chunking respects word boundaries.

    Args:
        text (String): The String field the text of which is to be chunked.
        chunk_size (int | None, optional): The maximum size of each chunk in characters. Defaults to None, which means
        effectively using 250.
        chunk_overlap (int | None, optional): The maximum overlap between chunks in characters. Defaults to None, which
        means effectively using {}.
        split_chars_keep: Characters to split at, but also keep in the text. Should be characters that can signal
        meaningful breakpoints in the text. Effectively defaults to ["!", "?", "."].
        split_chars_remove: Characters to split at and remove from the text. Should be characters that can signal
        meaningful breakpoints in the text. Effectively defaults to ["\n"].

    Returns:
        ChunkingNode: The chunking node.
    """
    return ChunkingNode(
        SchemaFieldNode(text),
        chunk_size,
        chunk_overlap,
        split_chars_keep,
        split_chars_remove,
    )
