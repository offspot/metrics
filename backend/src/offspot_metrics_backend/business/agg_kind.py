from enum import Enum


class AggKind(Enum):
    """The various kind of supported aggregations"""

    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    YEAR = "Y"
