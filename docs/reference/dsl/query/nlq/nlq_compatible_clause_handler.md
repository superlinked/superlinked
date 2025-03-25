Module superlinked.framework.dsl.query.nlq.nlq_compatible_clause_handler
========================================================================

Classes
-------

`NLQCompatibleClauseHandler(clause: QueryClause)`
:   NLQCompatibleClauseHandler(clause: 'QueryClause')

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.query.query_clause.query_clause.NLQCompatible
    * abc.ABC

    ### Static methods

    `from_clauses(clauses: Sequence[QueryClause]) ‑> list[superlinked.framework.dsl.query.nlq.nlq_compatible_clause_handler.NLQCompatibleClauseHandler]`
    :

    ### Instance variables

    `annotation_by_space_annotation: dict[str, str]`
    :

    `clause: superlinked.framework.dsl.query.query_clause.query_clause.QueryClause`
    :

    `is_type_mandatory_in_nlq: bool`
    :

    `nlq_annotations: list[NLQAnnotation]`
    :

    `nlq_compatible_clause: NLQCompatible`
    :

    ### Methods

    `get_allowed_values(self, param: TypedParam | Evaluated[TypedParam]) ‑> set[collections.abc.Sequence[str] | collections.abc.Sequence[float] | PIL.Image.Image | str | int | float | bool | tuple[str | None, str | None] | None]`
    :