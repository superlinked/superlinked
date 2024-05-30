Module superlinked.framework.dsl.space.custom_space
===================================================

Classes
-------

`CustomSpace(vector: superlinked.framework.common.schema.schema_object.FloatList | list[superlinked.framework.common.schema.schema_object.FloatList], length: int, aggregation: superlinked.framework.dsl.space.custom_space.CustomSpace.AggregationStrategy = AggregationStrategy.SUM_AND_NORMALIZE)`
:   CustomSpace is the instrument of ingesting your own vectors into Superlinked.
    This way you can use your own vectors right away. What you need to know: (you can use numbering too)
    - vectors need to have the same length
    - vectors will be L2Norm normalized to ensure weighting makes sense
    - weighting can be performed (query-time)
    - you are going to need an FloatList typed SchemaField to supply your data
    - the FloatList field will be able to parse any Sequence[float | int]
    - you can leave the aggregation parameter as default, or switch it to using vector averaging during aggregation.
    
    Initializes a CustomSpace for vector storage and manipulation within Superlinked.
    
    This constructor sets up a space designed for custom vector ingestion, allowing users to specify how these
    vectors are aggregated and normalized.
    
    Args:
        vector (FloatList | list[FloatList]): The input vector(s) to be stored in the space.
          This can be a single FloatList SchemaField or a list of those.
        length (int): The fixed length that all vectors in this space must have. This ensures uniformity and
          consistency in vector operations.
        aggregation (AggregationStrategy, optional): The strategy to use for aggregating multiple vectors.
          This can be either `SUM_AND_NORMALIZE` for summing vectors and normalizing to unit length,
          or `VECTOR_AVERAGE` for averaging vectors during aggregation, but not performing other normalization.
          Defaults to `SUM_AND_NORMALIZE`.
    
    Raises:
        InvalidAggregationStrategyException: If the specified aggregation strategy is not recognized. This ensures
          that only valid aggregation strategies are used.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC

    ### Class variables

    `AggregationStrategy`
    :   Controls how the supplied vectors are aggregated and normalized under the hood. Choose the option most suitable
        for your custom vectors:
            - sum_and_normalize: during aggregation, vectors are summed up elementwise, and normalized using L2 norm
              of the vector to achieve unit vector length when needed.
            - vector_average: vectors are summed up elementwise in case of aggregation, and normalized using the
              number of the aggregated vectors to achieve < 1 length.
              This policy expects vectors that are roughly unit length. Use it for vectors that are incompatible with L2
              normalization.