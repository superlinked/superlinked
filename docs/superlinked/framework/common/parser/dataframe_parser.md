Module superlinked.framework.common.parser.dataframe_parser
===========================================================

Classes
-------

`DataFrameParser(schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None)`
:   DataFrameParser gets a `pd.DataFrame` and using column-string mapping
    it transforms the `DataFrame` to a desired schema.
    
    Initizalize DataParser
    
    Get the desired output schema and initialize a default mapping
    that can be extended by DataParser realizations.
    
    Args:
        schema (IdSchemaObjectT): SchemaObject describing the desired output.
        mapping (Mapping[SchemaField, str], optional): Realizations can use the `SchemaField` to `str` mapping
            to define their custom mapping logic.
    
    Raises:
        InitializationException: Parameter `schema` is of invalid type.

    ### Ancestors (in MRO)

    * superlinked.framework.common.parser.data_parser.DataParser
    * abc.ABC
    * typing.Generic

    ### Methods

    `marshal(self, parsed_schemas: ParsedSchema | list[ParsedSchema]) ‑> pandas.core.frame.DataFrame`
    :   Converts a list of ParsedSchema objects into a pandas DataFrame.
        You can use this functionality to check, if your mapping was defined properly.
        
        Args:
            parsed_schemas (ParsedSchema | list[ParsedSchema]): A single ParsedSchema object
                or a list of ParsedSchema objects that you get
                after unmarshaling your `DataFrame`.
        
        Returns:
            pd.DataFrame: A DataFrame representation of the parsed schemas.

    `unmarshal(self, data: pd.DataFrame) ‑> list[superlinked.framework.common.parser.parsed_schema.ParsedSchema]`
    :   Parses the given DataFrame into a list of ParsedSchema objects according to the defined schema and mapping.
        
        Args:
            data (pd.DataFrame): Pandas DataFrame input.
        
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.