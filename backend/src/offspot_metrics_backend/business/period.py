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

    @classmethod
    def from_timestamp(cls, ts: int) -> "Period":
        return Period(datetime.fromtimestamp(ts))

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
        if agg_kind == AggKind.DAY:
            return f"{self.dt.year:04}-{self.month:02}-{self.day:02}"
        if agg_kind == AggKind.WEEK:
            return f"{self.dt.year:04} W{self.week:02}"
        if agg_kind == AggKind.MONTH:
            return f"{self.dt.year:04}-{self.month:02}"
        if agg_kind == AggKind.YEAR:
            return f"{self.year:04}"
        raise AttributeError

    def get_interval(self, agg_kind: AggKind) -> Interval:
        if agg_kind == AggKind.DAY:
            start = datetime(year=self.year, month=self.month, day=self.day)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=1)).timestamp()),
            )
        if agg_kind == AggKind.WEEK:
            start = datetime(
                year=self.year, month=self.month, day=self.day
            ) + timedelta(days=1 - self.weekday)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=7)).timestamp()),
            )
        if agg_kind == AggKind.MONTH:
            start = datetime(year=self.year, month=self.month, day=1)
            stop = datetime(year=self.year, month=self.month + 1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        if agg_kind == AggKind.YEAR:
            start = datetime(year=self.year, month=1, day=1)
            stop = datetime(year=self.year + 1, month=1, day=1)
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        raise AttributeError
