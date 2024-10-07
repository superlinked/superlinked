Module superlinked.framework.common.parser.data_parser
======================================================

Classes
-------

`DataParser(schema: IdSchemaObjectT, mapping: Mapping[SchemaField, str] | None = None)`
:   A DataParser describes the interface to get a source data to the format of a defined schema with mapping support.
    
    Attributes:
        mapping (Mapping[SchemaField, str], optional): Source to SchemaField mapping rules
            as `SchemaField`-`str` pairs such as `{movie_schema.title: "movie_title"}`.
    
    Initialize DataParser
    
    Get the desired output schema and initialize a default mapping
    that can be extended by DataParser realizations.
    
    Args:
        schema (IdSchemaObjectT): SchemaObject describing the desired output.
        mapping (Mapping[SchemaField, str], optional): Realizations can use the `SchemaField` to `str` mapping
            to define their custom mapping logic.
    
    Raises:
        InitializationException: Parameter `schema` is of invalid type.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * superlinked.framework.common.parser.dataframe_parser.DataFrameParser
    * superlinked.framework.common.parser.json_parser.JsonParser

    ### Methods

    `marshal(self, parsed_schemas: ParsedSchema | list[ParsedSchema]) ‑> list[~SourceTypeT]`
    :   Get a previously parsed data and return it to it's input format.
        
        Args:
            parsed_schemas: Previously parsed data that follows the schema of the `DataParser`.
        
        Returns:
            list[SourceTypeT]: A list of the original source data format after marshalling the parsed data.

    `unmarshal(self, data: SourceTypeT) ‑> list[superlinked.framework.common.parser.parsed_schema.ParsedSchema]`
    :   Get the source data and parse it to the desired Schema with the defined mapping.
        
        Args:
            data (TSourceType): Source data that corresponds to the DataParser's type.
        
        Returns:
            list[ParsedSchema]: A list of ParsedSchema objects.