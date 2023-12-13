Module superlinked.framework.dsl.space.recency_space
====================================================

Classes
-------

`RecencySpace(timestamp: superlinked.framework.common.schema.schema_object.Timestamp | list[superlinked.framework.common.schema.schema_object.Timestamp], period_time_param_list: list[superlinked.framework.common.dag.period_time_param.PeriodTimeParam] | superlinked.framework.common.dag.period_time_param.PeriodTimeParam | None = None, negative_filter: float = 0.0)`
:   Recency space is utilised to encode how recent items are. Use period_time_param_list
    to mark the time periods of interest.
    Items older than the largest period_time are going to have uniform recency score. (0 or negative_filter if set)
    You can use multiple period_times to give additional emphasis to sub time periods.
    Like using 2 days and 5 days gives extra emphasis to the first 2 days. The extent of which can be controlled with
    the respective weight parameters.
    Unit weights would give double emphasis on the first 2 days, 1 and 0.1 weights respectively
    would give tenfold importance to the first 2 days.
    All items older than 5 days would get 0 or `negative_filter` recency score.
    
    Attributes:
        timestamp (SpaceFieldSet): A set of Timestamp objects.
        It is a SchemaFieldObject not regular python ints or floats.
        period_time_param_list (list[PeriodTimeParam] | None): A list of period time parameters.
        Weights default to 1. Period time to 14 days.
        timestamp (SpaceFieldSet): A set of Timestamp objects.
        It is a SchemaFieldObject, not regular python ints or floats.
        period_time_param_list (list[PeriodTimeParam] | None): A list of period time parameters.
        Weights default to 1.0.
    
    Initialize the RecencySpace.
    
    Args:
        timestamp (Timestamp | list[Timestamp]): A timestamp or a list of timestamps.
        period_time_param_list (list[PeriodTimeParam] | None, optional): A list of period time parameters.
        Defaults to None.
        negative_filter (float): The recency score attributed to items older than the largest period_time value.
        Defaults to 0.0.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.space.space.Space
    * abc.ABC