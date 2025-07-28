Module superlinked.framework.common.parser.json_parser
======================================================

Classes
-------

`JsonParser(schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None)`
:   JsonParser gets a `Json` object and using `str` based dot separated path mapping
    it transforms the `Json` to a desired schema.
    
    Initialize DataParser
    
    Get the desired output schema and initialize a default mapping
    that can be extended by DataParser realizations.
    
    Args:
        schema (IdSchemaObjectT): SchemaObject describing the desired output.
        mapping (Mapping[SchemaField, str], optional): Realizations can use the `SchemaField` to `str` mapping
            to define their custom mapping logic.
    
    Raises:
        InvalidInputException: Parameter `schema` is of invalid type.

    ### Ancestors (in MRO)

    * superlinked.framework.common.parser.data_parser.DataParser
    * abc.ABC
    * typing.Generic

    ### Methods

    `unmarshal(self, data: dict[str, Any] | Sequence[dict[str, Any]]) ‑> list[superlinked.framework.common.parser.parsed_schema.ParsedSchema]`
    :   Parses the given Json into a list of ParsedSchema objects according to the defined schema and mapping.
        
        Args:
            data (Json): The Json representation of your data.
        
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects that will be processed by the spaces.