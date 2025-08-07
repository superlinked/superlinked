Module superlinked.framework.dsl.query.query_clause.space_weight_map
====================================================================

Classes
-------

`SpaceWeightMap(space_weights: Mapping[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]] = <factory>)`
:   SpaceWeightMap(space_weights: collections.abc.Mapping[superlinked.framework.dsl.space.space.Space, typing.Union[superlinked.framework.dsl.query.typed_param.TypedParam, superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]]] = <factory>)

    ### Ancestors (in MRO)

    * collections.abc.Mapping
    * collections.abc.Collection
    * collections.abc.Sized
    * collections.abc.Iterable
    * collections.abc.Container

    ### Instance variables

    `params: Sequence[superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]]`
    :

    `space_weights: Mapping[superlinked.framework.dsl.space.space.Space, superlinked.framework.dsl.query.typed_param.TypedParam | superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]]`
    :

    ### Methods

    `alter_param_values(self, param_values: Mapping[str, collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | tuple[str | None, str | None] | None], is_override_set: bool) ‑> Self | None`
    :

    `extend(self, weight_param_by_space: Mapping[superlinked.framework.dsl.space.space.Space, float | int | superlinked.framework.dsl.query.param.Param], all_space: Sequence[superlinked.framework.dsl.space.space.Space]) ‑> Self`
    :

    `set_param_name_if_unset(self, prefix: str) ‑> None`
    :