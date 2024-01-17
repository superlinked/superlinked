Module superlinked.framework.common.dag.period_time
===================================================

Classes
-------

`PeriodTime(period_time: datetime.timedelta, weight: float = 1.0)`
:   A class representing a period time parameter.
    Attributes:
        period_time (timedelta): Oldest item the parameter will differentiate. Older items will have
            0 or `negative_filter` recency_score.
        weight (float): Defaults to 1.0. Useful to tune different period_times against each other.
    
    Initialize the PeriodTime.
    Args:
        period_time (timedelta): Oldest item the parameter will differentiate.
            Older items will have 0 or `negative_filter` recency_score.
        weight (float, optional): Defaults to 1.0. Useful to tune different period_times against each other.