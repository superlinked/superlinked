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


import os
from datetime import datetime

from beartype.typing import Any, Mapping, Sequence
from graphviz import Digraph

from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.settings import settings


class DagVisualizer:
    def __init__(self, visualization_id: str) -> None:
        self.__visualization_id = visualization_id

    def visualize_evaluation(
        self, nodes: Sequence[Node], node_outputs: Mapping[str, Sequence[Any] | Exception]
    ) -> None:
        if not nodes:
            return
        dot = Digraph(comment="Dag Evaluation Visualization")
        dot.attr(size="12,12", fontname="Courier New", nodesep="0.5", ranksep="0.5")
        for node in nodes:
            self._print_node(node, node_outputs, dot)
        self._print_missing_parents(nodes, dot)
        self._print_edges(nodes, dot)
        filepath = self._calculate_file_path()
        dot.render(filepath, format="pdf", cleanup=True)

    def _calculate_file_path(self) -> str:
        timestamp = datetime.now().isoformat(timespec="milliseconds").replace(":", "_")
        filename = f"dag_eval_{self.__visualization_id}_{timestamp}"
        output_dir = settings.DAG_VISUALIZATION_OUTPUT_DIR or os.getcwd()
        filepath = f"{output_dir}/{filename}"
        return filepath

    @classmethod
    def _print_node(cls, node: Node, node_outputs: Mapping[str, Sequence[Any] | Exception], dot: Digraph) -> None:
        config_str = cls._format_config(node._get_node_id_parameters())
        output_str = cls._format_output_text(node, node_outputs)
        html_label = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
                <TR><TD BGCOLOR="#EEEEEE" ALIGN="CENTER"><B>{type(node).__name__}({node.node_id})</B></TD></TR>
                <TR><TD ALIGN="LEFT">{config_str}</TD></TR>
                <TR><TD ALIGN="LEFT">{output_str}</TD></TR>
            </TABLE>
        >"""
        dot.node(node.node_id, html_label, shape="none", color="black", penwidth="1", width="5")

    @classmethod
    def _format_output_text(cls, node: Node, node_outputs: Mapping[str, Sequence[Any] | Exception]) -> str:
        if node.node_id in node_outputs:
            node_output = node_outputs[node.node_id]
            if isinstance(node_output, Exception):
                output_values = [f"<B>{type(node_output).__name__}:</B> {cls._format_output_value(node_output)}"]
            else:
                output_values = [cls._format_output_value(value) for value in node_output]
            return "<BR ALIGN='LEFT'/>".join(output_values) + "<BR ALIGN='LEFT'/>"
        return "<I>No output</I>"

    @classmethod
    def _print_edges(cls, nodes: Sequence[Node], dot: Digraph) -> None:
        for node in nodes:
            for parent in node.parents:
                dot.edge(parent.node_id, node.node_id)

    @classmethod
    def _print_missing_parents(cls, nodes: Sequence[Node], dot: Digraph) -> None:
        node_ids_in_graph = {node.node_id for node in nodes}
        missing_parents = {
            parent for node in nodes for parent in node.parents if parent.node_id not in node_ids_in_graph
        }

        for parent in missing_parents:
            html_label = f"""<
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
                    <TR><TD BGCOLOR="#EEEEEE" ALIGN="CENTER"><B>{type(parent).__name__}({parent.node_id})</B></TD></TR>
                    <TR><TD ALIGN="LEFT"><I>Not Evaluated</I></TD></TR>
                </TABLE>
            >"""
            dot.node(parent.node_id, html_label, shape="none", color="gray", penwidth="1", width="5", style="dashed")

    @classmethod
    def _format_config(cls, data: dict[str, Any], indent: int = 0) -> str:
        def format_complex_value(value: str) -> str:
            if "(" in value and ")" in value and len(value) > 80:
                parts, current_part, depth = [], "", 0
                for char in value:
                    current_part += char
                    if char == "(":
                        depth += 1
                        if depth > 1:
                            continue
                        parts.append(current_part)
                        current_part = ""
                    elif char == "," and depth == 1:
                        parts.append(current_part)
                        current_part = ""
                    elif char == ")":
                        depth -= 1
                if current_part:
                    parts.append(current_part)
                indented_parts = ['<BR ALIGN="LEFT"/>&#160;&#160;&#160;&#160;'.join(parts[:-1])]
                if parts:
                    indented_parts.append(f'<BR ALIGN="LEFT"/>&#160;&#160;&#160;&#160;{parts[-1]}')
                return "".join(indented_parts)
            return value

        result = []
        for k, v in data.items():
            if isinstance(v, dict):
                result.append(f"{k}:")
                result.append(cls._format_config(v, indent + 2))
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                result.append(f"{k}:")
                for item in v:
                    result.append(f"- {cls._format_config(item, indent + 4)}")
            else:
                str_v = cls._escape_html(str(v))
                formatted_value = format_complex_value(str_v)
                result.append(f"{k}: {formatted_value}")

        return '<BR ALIGN="LEFT"/>'.join(result) + "<BR ALIGN='LEFT'/>"

    @classmethod
    def _format_output_value(cls, value: Any) -> str:
        value_as_str = str(value)
        value_as_str = '""' if value_as_str == "" else value_as_str
        return cls._escape_html(cls._truncate_long_text(value_as_str))

    @classmethod
    def _escape_html(cls, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&#39;")
            .replace('"', "&quot;")
            .replace("\n", "<BR/>")
        )

    @classmethod
    def _truncate_long_text(cls, text: str) -> str:
        max_length = 200
        if len(text) > max_length:
            return text[: max_length - 3] + "..."
        return text
