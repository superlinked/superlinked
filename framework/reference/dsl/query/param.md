Module superlinked.framework.dsl.query.param
============================================

Classes
-------

`Param(name: str, description: str | None = None, default: ParamInputType | None = None, options: Sequence[ParamInputType | None] | None = None)`
:   Class representing a parameter that will be provided during the execution of the query.
    
    Attributes:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (ParamInputType | None, optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.
        options (list[ParamInputType] | set[ParamInputType] | None, optional): Allowed values for this parameter.
            If provided, only these values will be accepted. Defaults to None.
    
    Initialize the Param.
    
    Args:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (ParamInputType, | None optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.
        options (list[ParamInputType] | set[ParamInputType] | None, optional): Allowed values for this parameter.
            If provided, only these values will be accepted. Defaults to None.

    ### Static methods

    `init_default(default: ParamInputType | None = None) ‑> superlinked.framework.dsl.query.param.Param`
    :