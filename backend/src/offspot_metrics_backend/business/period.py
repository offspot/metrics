import datetime
from dataclasses import dataclass

from dateutil.relativedelta import relativedelta

from offspot_metrics_backend.business.agg_kind import AggKind


@dataclass
class Interval:
    """A dataclass holding an interval start and stop timestamp"""

    start: int
    stop: int


@dataclass
class Period:
    """A processing period

    A processing period lasts one hour. All events happening in the samed period are
    aggregated in a single indicator state and then transformed into a record"""

    dt: datetime.datetime

    def __post_init__(self):
        self.dt = datetime.datetime.combine(self.dt.date(), datetime.time(self.dt.hour))

    @classmethod
    def from_timestamp(cls, ts: int) -> "Period":
        """Transform a timestamp into a period

        timestamp (ts) is the number of seconds since Unix epoch
        """
        return Period(datetime.datetime.fromtimestamp(ts))

    @property
    def year(self) -> int:
        """Return the period year"""
        return self.dt.year

    @property
    def month(self) -> int:
        """Return the period month"""
        return self.dt.month

    @property
    def day(self) -> int:
        """Return the period day"""
        return self.dt.day

    @property
    def hour(self) -> int:
        """Return the period hour"""
        return self.dt.hour

    @property
    def week(self) -> int:
        """Return the period week number (ISO)"""
        return self.dt.isocalendar().week

    @property
    def weekday(self) -> int:
        """Return the period day of the week (ISO)"""
        return self.dt.isoweekday()

    @property
    def timestamp(self) -> int:
        """Transform the period into a timestamp"""
        return int(self.dt.timestamp())

    def get_shifted(self, delta: relativedelta) -> "Period":
        """Return a new period shifted from delta"""
        return Period(self.dt + delta)

    def get_truncated_value(self, agg_kind: AggKind) -> str:
        """Truncate the period to corresponding day, week, month, year."""
        if agg_kind == AggKind.DAY:
            return f"{self.dt.year:04}-{self.month:02}-{self.day:02}"
        if agg_kind == AggKind.WEEK:
            return f"{self.dt.year:04} W{self.week:02}"
        if agg_kind == AggKind.MONTH:
            return f"{self.dt.year:04}-{self.month:02}"
        if agg_kind == AggKind.YEAR:
            return f"{self.year:04}"

        # we should never get there except if the enum is modified and we
        # forget to modify this function
        raise AttributeError  # pragma: no cover

    @classmethod
    def from_truncated_value(cls, truncated_value: str, agg_kind: AggKind) -> "Period":
        """Transform a truncated value into a period

        First period of the truncated value is returned.

        Examples:
        - "2023" + YEAR => "2023-01-01 00:00:00"
        - "2023-12" + MONTH => "2023-12-01 00:00:00",
        - "2023 W12 + WEEK => "2023-03-20 00:00:00"
        - "2023-12-25" + DAY => "2023-12-25 00:00:00",
        """

        def get_period(value: str, timeformat: str) -> Period:
            return Period(
                datetime.datetime.strptime(value, timeformat).replace(
                    tzinfo=datetime.UTC
                )
            )

        if agg_kind == AggKind.DAY:
            return get_period(truncated_value, "%Y-%m-%d")
        elif agg_kind == AggKind.WEEK:
            return get_period(f"{truncated_value} 1", "%Y W%W %w")
        elif agg_kind == AggKind.MONTH:
            return get_period(f"{truncated_value}-01", "%Y-%m-%d")
        elif agg_kind == AggKind.YEAR:  # pragma: no branch
            return get_period(f"{truncated_value}-01-01", "%Y-%m-%d")

    def get_interval(self, agg_kind: AggKind) -> Interval:
        """Transform the period into an interval matching the kind of aggregation

        E.g. for a weekly aggregation, the interval will start at the beginning and
        finish at the end of the week enclosing the period"""
        if agg_kind == AggKind.DAY:
            start = datetime.datetime(
                year=self.year,
                month=self.month,
                day=self.day,
                tzinfo=datetime.UTC,
            )
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + datetime.timedelta(days=1)).timestamp()),
            )
        if agg_kind == AggKind.WEEK:
            start = datetime.datetime(
                year=self.year, month=self.month, day=self.day, tzinfo=datetime.UTC
            ) - datetime.timedelta(days=self.weekday - 1)
            return Interval(
                start=int(start.timestamp()),
                stop=int((start + datetime.timedelta(days=7)).timestamp()),
            )
        if agg_kind == AggKind.MONTH:
            start = datetime.datetime(
                year=self.year, month=self.month, day=1, tzinfo=datetime.UTC
            )
            if self.month <= 11:  # noqa PLR2004
                stop = datetime.datetime(
                    year=self.year, month=self.month + 1, day=1, tzinfo=datetime.UTC
                )
            else:
                stop = datetime.datetime(
                    year=self.year + 1, month=1, day=1, tzinfo=datetime.UTC
                )
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        if agg_kind == AggKind.YEAR:
            start = datetime.datetime(
                year=self.year, month=1, day=1, tzinfo=datetime.UTC
            )
            stop = datetime.datetime(
                year=self.year + 1, month=1, day=1, tzinfo=datetime.UTC
            )
            return Interval(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )

        # we should never get there except if the enum is modified and we
        # forget to modify this function
        raise AttributeError  # pragma: no cover


class Now:
    def __init__(self) -> None:
        self.datetime = datetime.datetime.now()  # noqa: DTZ005
        self.period = Period(self.datetime)
        self.tick = Tick(self.datetime)


@dataclass
class Tick:
    """A processing tick

    A processing tick occurs every minutes"""

    dt: datetime.datetime

    def __post_init__(self):
        self.dt = datetime.datetime.combine(
            self.dt.date(), datetime.time(hour=self.dt.hour, minute=self.dt.minute)
        )
