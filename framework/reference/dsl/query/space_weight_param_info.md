Module superlinked.framework.dsl.query.space_weight_param_info
==============================================================

Classes
-------

`SpaceWeightParamInfo(global_param_name_by_space: Mapping[Space, str], param_names_by_space: Mapping[Space, Sequence[str]])`
:   SpaceWeightParamInfo(global_param_name_by_space: 'Mapping[Space, str]', param_names_by_space: 'Mapping[Space, Sequence[str]]')

    ### Static methods

    `from_clauses(clauses: Sequence[QueryClause]) ‑> superlinked.framework.dsl.query.space_weight_param_info.SpaceWeightParamInfo`
    :

    ### Instance variables

    `global_param_name_by_space: Mapping[superlinked.framework.dsl.space.space.Space, str]`
    :

    `param_names_by_space: Mapping[superlinked.framework.dsl.space.space.Space, Sequence[str]]`
    :

    ### Methods

    `get_weight_param_names(self) ‑> list[str]`
    :