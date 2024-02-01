import datetime
from dataclasses import dataclass


class Input:
    """A generic input interface"""

    ...


@dataclass(eq=True, frozen=True)
class TimedInput(Input):
    """Input with information about when it happened"""

    # moment where the input occured
    ts: datetime.datetime


@dataclass(eq=True, frozen=True)
class CountInput(Input):
    """An input with a number of items"""

    # number of items
    count: int
