from dataclasses import dataclass
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from .agg_kind import AggKind


@dataclass
class Interval:
    start: int
    stop: int


@dataclass
class Period:
    dt: datetime

    def __init__(self, dt: datetime) -> None:
        self.dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)

    @property
    def year(self) -> int:
        return self.dt.year

    @property
    def month(self) -> int:
        return self.dt.month

    @property
    def day(self) -> int:
        return self.dt.day

    @property
    def hour(self) -> int:
        return self.dt.hour

    @property
    def week(self) -> int:
        return self.dt.isocalendar().week

    @property
    def weekday(self) -> int:
        return self.dt.isoweekday()

    @property
    def timestamp(self) -> int:
        return int(self.dt.timestamp())

    def get_shifted(self, delta: relativedelta) -> "Period":
        return Period(self.dt + delta)

    def get_truncated_value(self, agg_kind: AggKind) -> str:
        if agg_kind == AggKind.D:
            return f"{self.dt.year:04}-{self.month:02}-{self.day:02}"
        if agg_kind == AggKind.W:
            return f"{self.dt.year:04} W{self.week:02}"
        if agg_kind == AggKind.M:
            return f"{self.dt.year:04}-{self.month:02}"
        if agg_kind == AggKind.Y:
            return f"{self.year:04}"
        raise AttributeError

    def get_interval(self, agg_kind: AggKind) -> Interval:
        if agg_kind == AggKind.D:
            start = datetime(year=self.year, month=self.month, day=self.day)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=1)).timestamp()),
            )
        if agg_kind == AggKind.W:
            start = datetime(
                year=self.year, month=self.month, day=self.day
            ) + timedelta(days=1 - self.weekday)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=7)).timestamp()),
            )
        if agg_kind == AggKind.M:
            start = datetime(year=self.year, month=self.month, day=1)
            stop = datetime(year=self.year, month=self.month + 1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        if agg_kind == AggKind.Y:
            start = datetime(year=self.year, month=1, day=1)
            stop = datetime(year=self.year + 1, month=1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        raise AttributeError
