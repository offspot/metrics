from dataclasses import dataclass
from datetime import datetime

from dateutil.relativedelta import relativedelta


@dataclass
class Period:
    year: int
    month: int
    day: int
    weekday: int
    week: int
    hour: int

    def __init__(self, dt: datetime) -> None:
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.weekday = dt.isoweekday()
        self.week = dt.isocalendar().week
        self.hour = dt.hour

    def get_datetime(self) -> datetime:
        return datetime.fromisoformat(
            f"{self.year:04}-{self.month:02}-{self.day:02} {self.hour:02}:00:00"
        )

    def get_shifted(self, delta: relativedelta) -> "Period":
        return Period(self.get_datetime() + delta)

    def get_truncated_value(self, kind: str) -> str:
        if kind == "D":
            return f"{self.year:04}-{self.month:02}-{self.day:02}"
        if kind == "W":
            return f"{self.year:04} W{self.week:02}"
        if kind == "M":
            return f"{self.year:04}-{self.month:02}"
        if kind == "Y":
            return f"{self.year:04}"
        raise AttributeError
