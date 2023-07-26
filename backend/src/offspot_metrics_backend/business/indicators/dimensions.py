from dataclasses import dataclass


@dataclass(frozen=True)
class DimensionsValues:
    value0: str | None
    value1: str | None
    value2: str | None
