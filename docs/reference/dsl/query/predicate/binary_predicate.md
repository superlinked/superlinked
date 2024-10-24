Module superlinked.framework.dsl.query.predicate.binary_predicate
=================================================================

Classes
-------

`LooksLikePredicate(left_param: superlinked.framework.common.schema.schema_object.SchemaField, right_param: collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | bool | None | tuple[str | None, str | None] | superlinked.framework.dsl.query.param.Param, weight: float | int | superlinked.framework.dsl.query.param.Param)`
:   QueryPredicate(op: ~OPT, params: list[superlinked.framework.common.schema.schema_object.SchemaField | superlinked.framework.dsl.query.param.Param | collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | None | tuple[str | None, str | None]], weight_param: float | int | superlinked.framework.dsl.query.param.Param)

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.predicate.binary_predicate.BinaryPredicate
    * superlinked.framework.dsl.query.predicate.query_predicate.QueryPredicate
    * typing.Generic

`SimilarPredicate(left_param: superlinked.framework.common.schema.schema_object.SchemaField, right_param: collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | bool | None | tuple[str | None, str | None] | superlinked.framework.dsl.query.param.Param, weight: float | int | superlinked.framework.dsl.query.param.Param, left_param_node: superlinked.framework.common.dag.node.Node)`
:   QueryPredicate(op: ~OPT, params: list[superlinked.framework.common.schema.schema_object.SchemaField | superlinked.framework.dsl.query.param.Param | collections.abc.Sequence[str] | collections.abc.Sequence[float] | str | int | float | None | tuple[str | None, str | None]], weight_param: float | int | superlinked.framework.dsl.query.param.Param)

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.predicate.binary_predicate.BinaryPredicate
    * superlinked.framework.dsl.query.predicate.query_predicate.QueryPredicate
    * typing.Generic