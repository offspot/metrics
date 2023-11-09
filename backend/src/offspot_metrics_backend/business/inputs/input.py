import datetime
from dataclasses import dataclass


class Input:
    """A generic input interface"""

    ...


@dataclass
class TimedInput(Input):
    """Input with information about when it happened"""

    # moment where the input occured
    ts: datetime.datetime
