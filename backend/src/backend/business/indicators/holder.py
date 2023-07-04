from dataclasses import dataclass
from typing import Generic, TypeVar

from backend.business.indicators import DimensionsValues

T = TypeVar("T")


@dataclass
class Holder(Generic[T]):
    """Generic data class for Record and State"""

    value: T
    dimensions: DimensionsValues

    def get_dimension_value(self, dimension: int) -> str | None:
        return self.dimensions[dimension] if len(self.dimensions) > dimension else None


@dataclass
class Record(Holder[int]):
    """Data class holding a record (recorder final value)"""


@dataclass
class State(Holder[str]):
    """Data class holding a state (recorder internal state)"""
