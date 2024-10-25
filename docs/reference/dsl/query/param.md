Module superlinked.framework.dsl.query.param
============================================

Classes
-------

`Param(name: str, description: str | None = None, default: Any | None = None)`
:   Class representing a parameter that will be provided during the execution of the query.
    
    Attributes:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (Any, optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.
    
    Initialize the Param.
    
    Args:
        name (str): The unique name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.
        default (Any, optional): Value to use if not overridden by query parameter.
            Natural language query will use defaults. Defaults to None.

    ### Static methods

    `init_default(default: Any | None = None) ‑> superlinked.framework.dsl.query.param.Param`
    :

    `init_evaluated(value: Any) ‑> superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.param.Param]`
    :