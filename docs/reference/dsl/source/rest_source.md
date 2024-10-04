Module superlinked.framework.dsl.source.rest_source
===================================================

Classes
-------

`RestSource(schema: ~IdSchemaObjectT, parser: superlinked.framework.common.parser.data_parser.DataParser | None = None, rest_descriptor: superlinked.framework.dsl.executor.rest.rest_descriptor.RestDescriptor | None = None)`
:   Abstract base class for generic types.
    
    A generic type is typically declared by inheriting from
    this class parameterized with one or more type variables.
    For example, a generic mapping type might be defined as::
    
      class Mapping(Generic[KT, VT]):
          def __getitem__(self, key: KT) -> VT:
              ...
          # Etc.
    
    This class can then be used as follows::
    
      def lookup_name(mapping: Mapping[KT, VT], key: KT, default: VT) -> VT:
          try:
              return mapping[key]
          except KeyError:
              return default

    ### Ancestors (in MRO)

    * superlinked.framework.online.source.online_source.OnlineSource
    * superlinked.framework.common.observable.TransformerPublisher
    * superlinked.framework.common.source.source.Source
    * typing.Generic

    ### Instance variables

    `path: str`
    :