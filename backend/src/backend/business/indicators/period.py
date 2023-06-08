from dataclasses import dataclass
from datetime import datetime


@dataclass
class Period:
    year: int
    month: int
    day: int
    weekday: int
    hour: int

    def __init__(self, dt: datetime) -> None:
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.weekday = dt.isoweekday()
        self.hour = dt.hour
