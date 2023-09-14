from dataclasses import dataclass


@dataclass(frozen=True)
class DimensionsValues:
    """A dataclass to hold dimension values"""

    value0: str | None
    value1: str | None
    value2: str | None
