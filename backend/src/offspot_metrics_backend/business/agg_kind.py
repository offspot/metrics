from enum import Enum


class AggKind(Enum):
    """The various kind of supported aggregations"""

    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    YEAR = "Y"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in AggKind]

    @classmethod
    def pattern(cls) -> str:
        return f'^{"|".join(cls.values())}$'
