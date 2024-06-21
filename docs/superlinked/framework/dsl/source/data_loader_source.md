Module superlinked.framework.dsl.source.data_loader_source
==========================================================

Classes
-------

`DataFormat(*args, **kwds)`
:   Create a collection of name/value pairs.
    
    Example enumeration:
    
    >>> class Color(Enum):
    ...     RED = 1
    ...     BLUE = 2
    ...     GREEN = 3
    
    Access them by:
    
    - attribute access::
    
    >>> Color.RED
    <Color.RED: 1>
    
    - value lookup:
    
    >>> Color(1)
    <Color.RED: 1>
    
    - name lookup:
    
    >>> Color['RED']
    <Color.RED: 1>
    
    Enumerations can be iterated over, and know how many members they have:
    
    >>> len(Color)
    3
    
    >>> list(Color)
    [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
    
    Methods can be added to enumerations, and members can have their own
    attributes -- see the documentation for details.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CSV`
    :

    `FWF`
    :

    `JSON`
    :

    `ORC`
    :

    `PARQUET`
    :

    `XML`
    :

`DataLoaderConfig(path: str, format: superlinked.framework.dsl.source.data_loader_source.DataFormat, name: str | None = None, pandas_read_kwargs: dict[str, typing.Any] | None = None)`
:   DataLoaderConfig(path: str, format: superlinked.framework.dsl.source.data_loader_source.DataFormat, name: str | None = None, pandas_read_kwargs: dict[str, typing.Any] | None = None)

    ### Class variables

    `format: superlinked.framework.dsl.source.data_loader_source.DataFormat`
    :

    `name: str | None`
    :

    `pandas_read_kwargs: dict[str, typing.Any] | None`
    :

    `path: str`
    :

`DataLoaderSource(schema: ~SchemaObjectT, data_loader_config: superlinked.framework.dsl.source.data_loader_source.DataLoaderConfig, parser: superlinked.framework.common.parser.data_parser.DataParser | None = None)`
:   Abstract base class for a source.
    
    Initialize the Source.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.source.source.Source
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `config: superlinked.framework.dsl.source.data_loader_source.DataLoaderConfig`
    :

    `name: str`
    :