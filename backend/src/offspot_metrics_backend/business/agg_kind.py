from enum import Enum


class AggKind(str, Enum):
    """The various kind of supported aggregations"""

    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    YEAR = "Y"

    @classmethod
    def values(cls) -> list[str]:
        """Returns all enum allowed values"""
        return [item.value for item in AggKind]

    @classmethod
    def pattern(cls) -> str:
        """Returns a regexp matching enum allowed values"""
        return f'^{"|".join(cls.values())}$'
