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

from __future__ import annotations

import inspect
from pydoc import locate

from beartype.typing import Any, Generic, Sequence, TypeVar, cast

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.exception import NotImplementedException

CompiledNodeT = TypeVar("CompiledNodeT")
ImportedNodeT = TypeVar("ImportedNodeT")


class CompiledNodeRegistry(Generic[CompiledNodeT]):
    _instance = None

    def __new__(cls, *_: Any) -> CompiledNodeRegistry[CompiledNodeT]:
        if cls._instance is None:
            cls._instance = super(CompiledNodeRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        base_node_type: type[CompiledNodeT],
        default_node_types: Sequence[type[CompiledNodeT]] | None = None,
    ) -> None:
        super().__init__()
        self._compiled_node_type_by_node_type = dict[type[Node], type[CompiledNodeT]]()
        self._base_node_type = base_node_type
        self._compiled_node_type_by_node_type = {
            CompiledNodeRegistry.get_node_type(node, base_node_type): node
            for node in default_node_types or []
        }

    @staticmethod
    def get_node_type(
        node_type: type[CompiledNodeT], base_node_type: type[CompiledNodeT]
    ) -> type[Node]:
        """
        Checks if CompiledNodeT child implements CompiledNodeT containing Node child Generic type.
        If yes, returns that Node child type.
        """
        node_bases = getattr(node_type, "__orig_bases__", [])
        for base in node_bases:
            if issubclass(base.__origin__, base_node_type):
                for arg in getattr(base, "__args__", []):
                    if inspect.isclass(arg) and issubclass(arg, Node):
                        return arg
                    origin = getattr(arg, "__origin__", None)
                    if origin and issubclass(origin, Node):
                        return origin
        raise NotImplementedException(
            f"Node type not found for {base_node_type.__name__}."
        )

    def register_node(
        self, node: type[Node], compiled_node: type[CompiledNodeT]
    ) -> None:
        self._compiled_node_type_by_node_type[node] = compiled_node

    def register_node_by_path(self, node_path: str, compiled_node_path: str) -> None:
        node_class = self.__import_node_class(node_path, Node)  # type: ignore[type-abstract]
        compiled_node_class = self.__import_node_class(
            compiled_node_path,
            self._base_node_type,  # type: ignore[type-abstract]
        )
        self._compiled_node_type_by_node_type[node_class] = compiled_node_class

    def __import_node_class(
        self, path: str, expected_class: type[ImportedNodeT]
    ) -> type[ImportedNodeT]:
        node_class = locate(path)
        if not isinstance(node_class, type):
            raise ValueError(f"Not a valid class path: {path}")
        if not issubclass(node_class, expected_class):
            raise ValueError(
                f"Not {expected_class.__name__} type: {node_class.__name__}"
            )
        return cast(type[ImportedNodeT], node_class)

    def init_compiled_node(
        self, node: Node, parents: Sequence[CompiledNodeT], *args: Any
    ) -> CompiledNodeT:
        compiled_node_class = self._compiled_node_type_by_node_type.get(type(node))
        if compiled_node_class is None:
            raise NotImplementedException(
                f"Not implemented Node type: {type(node).__name__}"
            )
        return compiled_node_class(node, parents, *args)  # type: ignore
