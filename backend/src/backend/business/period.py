from dataclasses import dataclass
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


@dataclass
class Interval:
    start: int
    stop: int


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

    def get_truncated_value(self, agg_kind: str) -> str:
        if agg_kind == "D":
            return f"{self.year:04}-{self.month:02}-{self.day:02}"
        if agg_kind == "W":
            return f"{self.year:04} W{self.week:02}"
        if agg_kind == "M":
            return f"{self.year:04}-{self.month:02}"
        if agg_kind == "Y":
            return f"{self.year:04}"
        raise AttributeError

    def get_interval(self, agg_kind: str) -> Interval:
        if agg_kind == "D":
            start = datetime(year=self.year, month=self.month, day=self.day)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=1)).timestamp()),
            )
        if agg_kind == "W":
            start = datetime(
                year=self.year, month=self.month, day=self.day
            ) + timedelta(days=1 - self.weekday)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=7)).timestamp()),
            )
        if agg_kind == "M":
            start = datetime(year=self.year, month=self.month, day=1)
            stop = datetime(year=self.year, month=self.month + 1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        if agg_kind == "Y":
            start = datetime(year=self.year, month=1, day=1)
            stop = datetime(year=self.year + 1, month=1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        raise AttributeError
