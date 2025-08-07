Module superlinked.framework.dsl.query.typed_param
==================================================

Classes
-------

`SchemaFieldToStrConverter()`
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

    * superlinked.framework.common.interface.type_converter.TypeConverter
    * typing.Generic
    * abc.ABC

    ### Methods

    `convert(self, base: SchemaField) ‑> str`
    :

`TypedParam(param: Param, valid_param_value_types: Sequence[TypeDescriptor])`
:   TypedParam(param: 'Param', valid_param_value_types: 'Sequence[TypeDescriptor]')

    ### Static methods

    `from_unchecked_types(param: Param, valid_param_value_types: Sequence[type]) ‑> superlinked.framework.dsl.query.typed_param.TypedParam`
    :

    `init_default(valid_param_value_types: Sequence[type], default: ParamInputType | None = None) ‑> superlinked.framework.dsl.query.typed_param.TypedParam`
    :

    `init_evaluated(valid_param_value_types: Sequence[type], value: Any) ‑> superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :

    ### Instance variables

    `param: superlinked.framework.dsl.query.param.Param`
    :

    `valid_param_value_types: Sequence[superlinked.framework.common.type_descriptor.TypeDescriptor]`
    :

    ### Methods

    `evaluate(self, value: Any) ‑> superlinked.framework.common.interface.evaluated.Evaluated[superlinked.framework.dsl.query.typed_param.TypedParam]`
    :