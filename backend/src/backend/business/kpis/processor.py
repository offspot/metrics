from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from backend.business.kpis.kpi import Kpi
from backend.business.kpis.value import Value
from backend.business.period import Period
from backend.db.persister import Persister


@dataclass
class Timestamps:
    start: int
    stop: int


class Processor:
    """A processor is responsible for transforming indicator records into kpis"""

    def __init__(self, now: Period) -> None:
        self.kpis: List[Kpi] = []
        self.current_period = now
        self.current_day = now.get_truncated_value("D")

    def process_tick(self, now: Period, session: Session) -> None:
        """Process a clock tick"""

        # if we are in the same period, nothing to do
        if self.current_period == now:
            return

        period_to_compute = self.current_period
        self.current_period = now
        # create/update KPIs values for every kind of aggregation period
        # that are update hourly
        for kpi in self.kpis:
            for kind in ["D", "W", "M"]:
                Processor.compute_kpi_values_for_kind(
                    now=period_to_compute, kpi=kpi, kind=kind, session=session
                )

        # create/update KPIs values for yearly aggregation period
        # which are updated only once per day
        now_day = now.get_truncated_value("D")
        if self.current_day != now_day:
            for kpi in self.kpis:
                Processor.compute_kpi_values_for_kind(
                    now=period_to_compute, kpi=kpi, kind="Y", session=session
                )
            self.current_day = now_day

    @classmethod
    def get_periods_to_keep(cls, kind: str, now: Period) -> List[str] | None:
        if kind == "D":
            return [
                now.get_shifted(relativedelta(days=-delta)).get_truncated_value(kind)
                for delta in range(0, 7)
            ]
        if kind == "W":
            return [
                now.get_shifted(relativedelta(weeks=-delta)).get_truncated_value(kind)
                for delta in range(0, 4)
            ]
        if kind == "M":
            return [
                now.get_shifted(relativedelta(months=-delta)).get_truncated_value(kind)
                for delta in range(0, 12)
            ]
        if kind == "Y":
            return None  # Special value meaning that all values are kept
        raise AttributeError

    @classmethod
    def compute_kpi_values_for_kind(
        cls, now: Period, kpi: Kpi, kind: str, session: Session
    ) -> None:
        """Compute KPI values and update DB accordingly

        This method act on a given KPI for a given kind of aggregation.
        Existing KPI values are updated in DB. New ones are created.
        Old ones are deleted"""
        values: List[Value] = Persister.get_kpi_values(
            kpi_id=kpi.unique_id, kind=kind, session=session
        )
        current_period = now.get_truncated_value(kind)
        periods_to_keep = Processor.get_periods_to_keep(kind, now)
        value_updated = False
        timestamps = cls.get_timestamps(kind=kind, now=now)
        for value in values:
            if periods_to_keep and value.period not in periods_to_keep:
                # delete old KPI values
                Persister.delete_kpi_value(
                    kpi_id=kpi.unique_id,
                    kind=kind,
                    period=value.period,
                    session=session,
                )
            if value.period == current_period:
                # update the existing KPI value
                value_updated = True
                value.value = kpi.get_value(
                    kind=kind,
                    start_ts=timestamps.start,
                    stop_ts=timestamps.stop,
                    session=session,
                )
                Persister.update_kpi_value(
                    kpi_id=kpi.unique_id,
                    kind=kind,
                    period=value.period,
                    value=value.value,
                    session=session,
                )
        if not value_updated:
            # create a new KPI value since there is no existing one
            value = Value(
                period=current_period,
                value=kpi.get_value(
                    kind=kind,
                    start_ts=timestamps.start,
                    stop_ts=timestamps.stop,
                    session=session,
                ),
            )
            Persister.add_kpi_value(
                kpi_id=kpi.unique_id,
                kind=kind,
                period=value.period,
                value=value.value,
                session=session,
            )

    @classmethod
    def get_timestamps(cls, kind: str, now: Period) -> Timestamps:
        if kind == "D":
            start = datetime(year=now.year, month=now.month, day=now.day)
            return Timestamps(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=1)).timestamp()),
            )
        if kind == "W":
            start = datetime(year=now.year, month=now.month, day=now.day) + timedelta(
                days=1 - now.weekday
            )
            return Timestamps(
                start=int(start.timestamp()),
                stop=int((start + timedelta(days=7)).timestamp()),
            )
        if kind == "M":
            start = datetime(year=now.year, month=now.month, day=1)
            stop = datetime(year=now.year, month=now.month + 1, day=1)
            return Timestamps(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        if kind == "Y":
            start = datetime(year=now.year, month=1, day=1)
            stop = datetime(year=now.year + 1, month=1, day=1)
            return Timestamps(
                start=int(start.timestamp()),
                stop=int(stop.timestamp()),
            )
        raise AttributeError

    def restore_from_db(self, session: Session) -> None:
        """Restore data from database, typically after a process restart"""

        # retrieve last known period from DB
        lastPeriod = Persister.get_last_current_period(session)

        # if there is no last period, nothing to do
        if not lastPeriod:
            return

        # create/update KPIs values for all aggregation period
        # which are updated once per hour
        print(self.current_period)
        print(lastPeriod)
        if lastPeriod != self.current_period:
            for kpi in self.kpis:
                for kind in ["D", "W", "M"]:
                    Processor.compute_kpi_values_for_kind(
                        now=lastPeriod, kpi=kpi, kind=kind, session=session
                    )

        # create/update KPIs values for yearly aggregation period
        # which are updated only once per day
        lastPeriod_day = lastPeriod.get_truncated_value("D")
        if self.current_day != lastPeriod_day:
            for kpi in self.kpis:
                Processor.compute_kpi_values_for_kind(
                    now=lastPeriod, kpi=kpi, kind="Y", session=session
                )
