from typing import Generic, TypeVar

from pydantic.dataclasses import dataclass

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues

T = TypeVar("T")


@dataclass
class Holder(Generic[T]):
    """Generic data class for Record and State"""

    value: T
    dimensions: DimensionsValues


@dataclass
class Record(Holder[int]):
    """Data class holding a record (recorder final value)"""


@dataclass
class State(Holder[str]):
    """Data class holding a state (recorder internal state)"""
