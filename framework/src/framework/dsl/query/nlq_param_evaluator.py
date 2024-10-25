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

from collections import defaultdict

from beartype.typing import Any, cast
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from superlinked.framework.common.exception import QueryException
from superlinked.framework.common.nlq.open_ai import OpenAIClient, OpenAIClientConfig
from superlinked.framework.common.schema.schema_object import Blob, SchemaField
from superlinked.framework.dsl.query.nlq_pydantic_model_builder import (
    NLQPydanticModelBuilder,
)
from superlinked.framework.dsl.query.query_clause import (
    HardFilterClause,
    LooksLikeFilterClause,
    SimilarFilterClause,
    SpaceWeightClause,
)
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor
from superlinked.framework.dsl.query.query_param_information import (
    ParamGroup,
    ParamInfo,
    WeightedParamInfo,
)
from superlinked.framework.dsl.space.space import Space

# Exclude from documentation.
__pdoc__ = {}
__pdoc__["NLQParamEvaluator"] = False

QUERY_MODEL_NAME = "QueryModel"


class NLQParamEvaluator:
    def __init__(self, query_descriptor: QueryDescriptor) -> None:
        self.param_infos = self.calculate_param_infos(query_descriptor)
        self.model_builder = NLQPydanticModelBuilder(self.param_infos)

    def calculate_param_infos(
        self, query_descriptor: QueryDescriptor
    ) -> list[ParamInfo]:
        space_weight_params = [
            ParamInfo.init_with(
                ParamGroup.SPACE_WEIGHT,
                clause.value_param,
                None,
                clause.space,
            )
            for clause in query_descriptor.get_clauses_by_type(SpaceWeightClause)
        ]
        hard_filter_params = [
            ParamInfo.init_with(
                ParamGroup.HARD_FILTER,
                clause.value_param,
                cast(SchemaField, clause.operand),
                None,
                clause.op,
            )
            for clause in query_descriptor.get_clauses_by_type(HardFilterClause)
        ]
        similar_filter_params = [
            WeightedParamInfo.init_with(
                ParamGroup.SIMILAR_FILTER_VALUE,
                ParamGroup.SIMILAR_FILTER_WEIGHT,
                clause.value_param,
                clause.weight_param,
                clause.schema_field,
                clause.space,
            )
            for clause in query_descriptor.get_clauses_by_type(SimilarFilterClause)
            if not isinstance(clause.schema_field, Blob)
        ]
        if (
            looks_like_clause := query_descriptor.get_clause_by_type(
                LooksLikeFilterClause
            )
        ) is not None:
            looks_like = WeightedParamInfo.init_with(
                ParamGroup.LOOKS_LIKE_FILTER_VALUE,
                ParamGroup.LOOKS_LIKE_FILTER_WEIGHT,
                looks_like_clause.value_param,
                looks_like_clause.weight_param,
                looks_like_clause.schema_field,
            )
        else:
            looks_like = None

        nested_params = [
            space_weight_params,
            hard_filter_params,
            [weighted.value_param for weighted in similar_filter_params],
            [weighted.weight_param for weighted in similar_filter_params],
            ([looks_like.value_param, looks_like.weight_param] if looks_like else []),
        ]
        return [param for param_list in nested_params for param in param_list]

    def evaluate_param_infos(
        self, natural_query: str, client_config: OpenAIClientConfig
    ) -> dict[str, Any]:
        if self._all_params_have_value_set():
            return {}
        model_class = self.model_builder.build()
        instructor_prompt = self._calculate_instructor_prompt(model_class)
        try:
            client = OpenAIClient(client_config)
            filled_values = client.query(natural_query, instructor_prompt, model_class)
            return filled_values
        except Exception as e:
            raise QueryException(f"Error executing natural query: {str(e)}") from e

    def _all_params_have_value_set(self) -> bool:
        return all(
            param_info.value is not None and not param_info.is_default
            for param_info in self.param_infos
        )

    def _calculate_instructor_prompt(self, model_class: type[BaseModel]) -> str:
        persona_description = """You are helping a user translate their natural language query to a structured
        Superlinked query. A Superlinked query is a knn search using a query vector, ran against a knowledgebase of items using
        cosine (dot-product) similarity.
        Steps to follow:\n
        1. Extract Key Elements: Identify important elements such as descriptions, recency, categorical, numerical
        or other textual data from the user query.\n
        2. Map Elements to Spaces: Assign these elements to the corresponding spaces provided below.\n
        3. Assign Weights and Values: Set appropriate weights and values based on user preferences. Use default values
        if not explicitly stated in the prompt.\n
        """
        context_text = """
        To achieve this you essentially need to extract weights and other values. The multimodal
        vectors are creating by vectorizing extracted query input values, concatenating them, and re-weighting them
        afterwards. Spaces are the abstractions holding the vectorized versions of inputs. Weights for .with_vector and
        .similar clauses essentially control their importance compared to each other, while space weights are applied on
        top of these, controlling the importance of each vector part, like text, numerical data, recency or categorical
        data - of which multiple can be present in each vector. So however high similar (or with_vector) clause weights
        are set if the corresponding space weight is low, they will have low effect.
        If the field is not related in any way to the user prompt, you can use the default value.
        If the user prompt is "I'm looking for a blue dog", search for a field that is related a color field and a field
        that is related to an animal, and set their values "blue" and "dog" respectively. Their weights should be equal
        and non-zero. If the user shows extra preference for an attribute, give them bigger weight. If a user expresses
        opposite preference, give that attribute negative weight. The name of the field, the corresponding "space" and
        "schema_field" can help identify what the field is used for. You will now get information about the spaces, and
        the corresponding parameters you can set to express user intent best.
        """
        affected_spaces_text = self._generate_affected_spaces_text(model_class)
        action_text = "Fill up the weights and values based on the user prompt if the default value is None/null."
        instructor_prompt = "\n####\n".join(
            (
                self._without_line_breaks(persona_description),
                self._without_line_breaks(context_text),
                affected_spaces_text,
                self._generate_helper_examples(),
                action_text,
            )
        )
        return instructor_prompt

    def _group_param_infos_by_space_and_annotation(
        self,
    ) -> dict[str, dict[Space, list[ParamInfo]]]:
        param_infos_by_space_by_annotation: defaultdict[
            str, defaultdict[Space, list[ParamInfo]]
        ] = defaultdict(lambda: defaultdict(list))
        for param_info in self.param_infos:
            if param_info.space is not None:
                annotation = self._without_line_breaks(param_info.space.annotation)
                param_infos_by_space_by_annotation[annotation][param_info.space].append(
                    param_info
                )
        return dict(param_infos_by_space_by_annotation)

    def _generate_affected_spaces_text(self, model_class: type[BaseModel]) -> str:
        param_infos_by_space_by_annotation = (
            self._group_param_infos_by_space_and_annotation()
        )
        param_infos_without_space = [
            param_info for param_info in self.param_infos if param_info.space is None
        ]
        space_related_text = (
            self._calculate_space_related_text(
                model_class, param_infos_by_space_by_annotation
            )
            if param_infos_by_space_by_annotation
            else None
        )
        non_space_related_text_with_description = (
            self._calculate_non_space_related_text(
                model_class, param_infos_without_space
            )
            if param_infos_without_space
            else None
        )
        return "\n###\n".join(
            part
            for part in (space_related_text, non_space_related_text_with_description)
            if part is not None
        )

    def _calculate_non_space_related_text(
        self, model_class: type[BaseModel], param_infos_without_space: list[ParamInfo]
    ) -> str:
        field_details_text = "\n".join(
            (
                self._calculate_field_details_text(model_class, param_info)
                for param_info in param_infos_without_space
            )
        )
        return (
            "Here are some details of the fields that need an exact value to be set"
            f" set:\n{field_details_text}"
        )

    def _calculate_space_related_text(
        self,
        model_class: type[BaseModel],
        param_infos_by_space_by_annotation: dict[str, dict[Space, list[ParamInfo]]],
    ) -> str:
        space_text = "\n##\n".join(
            (
                self._generate_space_text(annotation, param_infos_by_space, model_class)
                for annotation, param_infos_by_space in param_infos_by_space_by_annotation.items()
            )
        )
        return (
            f"Following are parameters grouped under the spaces they are corresponding to."
            f" Spaces are grouped too, if they have the same description. After the grouped spaces"
            f" come the description of the space. Subsequently the next space group follow:\n\n{space_text}"
        )

    def _generate_space_text(
        self,
        annotation: str,
        param_infos_by_space: dict[Space, list[ParamInfo]],
        model_class: type[BaseModel],
    ) -> str:
        space_field_text = "\n\n".join(
            (
                self._generate_space_field_text(space, param_infos, model_class)
                for space, param_infos in param_infos_by_space.items()
            )
        )
        return f"Grouped space names and params:\n{space_field_text}\n\nSpace description:\n{annotation}"

    def _generate_space_field_text(
        self, space: Space, param_infos: list[ParamInfo], model_class: type[BaseModel]
    ) -> str:
        field_details = "\n".join(
            (
                self._calculate_field_details_text(model_class, param_info)
                for param_info in param_infos
            )
        )
        return f"{type(space).__name__}_{hash(space)}:\n{field_details}"

    def _calculate_field_details_text(
        self, model_class: type[BaseModel], param_info: ParamInfo
    ) -> str:
        model_field_info = model_class.model_fields[param_info.name]
        is_weight_text = "weight" if param_info.is_weight else "value"
        field_detail_parts = [
            f" - {param_info.name} is a {is_weight_text}",
            (
                (
                    " that should only be filled if the user wants to explicitly filter to"
                    f" {param_info.op.value.replace('_', ' ')}"
                )
                if param_info.op
                else " to"
            ),
            f" {self._get_field_annotation(model_field_info)} type",
            (
                f" for the field named {param_info.schema_field.name}"
                if param_info.schema_field
                else ""
            ),
            (
                f" with the following description: {param_info.description}"
                if param_info.description
                else ""
            ),
        ]
        field_details_text = "".join(part for part in field_detail_parts if part)
        return field_details_text

    def _get_field_annotation(self, model_field_info: FieldInfo) -> str:
        if not model_field_info.annotation:
            return "any"
        annotation = str(model_field_info.annotation.__name__)
        return str(model_field_info.annotation) if annotation == "list" else annotation

    def _without_line_breaks(self, text: str) -> str:
        python_multiline_string_delimiter = "\n        "
        return text.replace(python_multiline_string_delimiter, " ")

    def _generate_helper_examples(self) -> str:
        examples_prompt_section: str = """Key advice:\n
        1. Try separating text referring to different text fields. "Comedy movies about gangsters" would mean a .similar
        clause corresponding the genre field would get the input "comedy" while the .similar clause of the description
        field would receive the input "gangsters". Their weight could be uniform 1.\n
        2. Think about recency in context with the space description. If they say old or recent movies, it is simple,
        the weight has to be negative or positive, respectively. Having a recency space spanning over 30 years, if
        the query asks for "drama movies from the 2010s", which are around 10-20 years old, the best you can do is set
        recency weight smaller compared to other weights (genre weight for drama), but positive.\n
        3. If adjectives are used, reflect them on the query. Absolute preference, excluding other options probably
        refers to a filter clause. If there are no filter clause, that space or clause should have higher weight, than
        the others. In the case of "Very recent action movies about the Cold War era" very recent would mean a higher
        recency weight than the genre space (with "action" input) and the description, or possibly setting space (with
        the input "Cold War era").\n
        4. When dealing with numbers, the Mode of the NumberSpace is of utmost importance. Also, sometimes number space
        references are a bit harder to extract. "High quality products" would mean positive weight for a rating, or
        the like space that conveys quality of the product - even though there is no direct reference to ratings or
        reviews. Conversely, if the space refers to how bad the product is, like number of complaints, high quality
        would mean a negative weight in that case.\n
        5. Categorical spaces can only have a limited set of values specified in the space description. If you see text
        present in the query that is present in the categorical similarity space description, it most probably refers to
        that space. Fill the corresponding .similar clause input with the value (multiple are possible) and give it
        positive weight - unless the query specifies preference against that category - in that case use a negative
        weight.\n
        """
        return self._without_line_breaks(examples_prompt_section)
