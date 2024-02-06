Module superlinked.framework.common.parser.json_parser
======================================================

Classes
-------

`JsonParser(schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None)`
:   JsonParser gets a `Json` object and using `str` based json path mapping
    it transforms the `Json` to a desired schema.
    
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

    `unmarshal(self, data: Json) ‑> list[superlinked.framework.common.parser.parsed_schema.ParsedSchema]`
    :   Parses the given Json into a list of ParsedSchema objects according to the defined schema and mapping.
        
        Args:
            data (Json): The Json representation of your data.
        
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.