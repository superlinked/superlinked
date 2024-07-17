Module superlinked.framework.dsl.query.param
============================================

Classes
-------

`Param(name: str, description: str | None = None)`
:   Class representing a parameter that will be provided during the execution of the query.
    
    Attributes:
        name (str): The name of the parameter.
    
    Initialize the Param.
    
    Args:
        name (str): The name of the parameter.
        description (str, optional): Description of the parameter. Used for natural language query.
            Defaults to None.