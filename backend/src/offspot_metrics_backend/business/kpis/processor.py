from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.value import Value
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.persister import Persister


class Processor:
    """A processor is responsible for transforming indicator records into kpis"""

    def __init__(self, current_period: Period) -> None:
        self.kpis: list[Kpi] = []
        self.current_period = current_period
        self.current_day = current_period.get_truncated_value(AggKind.DAY)

    def process_tick(self, tick_period: Period, session: Session) -> bool:
        """Process a clock tick

        Returns True if KPIs have been updated"""

        # if we are in the same period, nothing to do
        if self.current_period == tick_period:
            return False

        period_to_compute = self.current_period
        self.current_period = tick_period
        # create/update KPIs values for every kind of aggregation period
        # that are update hourly
        for kpi in self.kpis:
            for agg_kind in [AggKind.DAY, AggKind.WEEK, AggKind.MONTH]:
                Processor.compute_kpi_values_for_aggregation_kind(
                    now=period_to_compute, kpi=kpi, agg_kind=agg_kind, session=session
                )

        # create/update KPIs values for yearly aggregation period
        # which are updated only once per day
        tick_day = tick_period.get_truncated_value(AggKind.DAY)
        if self.current_day != tick_day:
            for kpi in self.kpis:
                Processor.compute_kpi_values_for_aggregation_kind(
                    now=period_to_compute,
                    kpi=kpi,
                    agg_kind=AggKind.YEAR,
                    session=session,
                )
            self.current_day = tick_day

        return True

    @classmethod
    def get_aggregations_to_keep(
        cls, agg_kind: AggKind, now: Period
    ) -> list[str] | None:
        if agg_kind == AggKind.DAY:
            return [
                now.get_shifted(relativedelta(days=-delta)).get_truncated_value(
                    agg_kind
                )
                for delta in range(0, 7)
            ]
        if agg_kind == AggKind.WEEK:
            return [
                now.get_shifted(relativedelta(weeks=-delta)).get_truncated_value(
                    agg_kind
                )
                for delta in range(0, 4)
            ]
        if agg_kind == AggKind.MONTH:
            return [
                now.get_shifted(relativedelta(months=-delta)).get_truncated_value(
                    agg_kind
                )
                for delta in range(0, 12)
            ]
        if agg_kind == AggKind.YEAR:
            return None  # Special value meaning that all values are kept
        raise AttributeError

    @classmethod
    def compute_kpi_values_for_aggregation_kind(
        cls, now: Period, kpi: Kpi, agg_kind: AggKind, session: Session
    ) -> None:
        """Compute KPI values and update DB accordingly

        This method act on a given KPI for a given kind of aggregation.
        Existing KPI values are updated in DB. New ones are created.
        Old ones are deleted"""
        values: list[Value] = Persister.get_kpi_values(
            kpi_id=kpi.unique_id, agg_kind=agg_kind, session=session
        )
        current_agg_value = now.get_truncated_value(agg_kind)
        aggregations_to_keep = Processor.get_aggregations_to_keep(agg_kind, now)
        value_updated = False
        timestamps = now.get_interval(agg_kind=agg_kind)
        for value in values:
            if aggregations_to_keep and value.agg_value not in aggregations_to_keep:
                # delete old KPI values
                Persister.delete_kpi_value(
                    kpi_id=kpi.unique_id,
                    agg_kind=agg_kind,
                    agg_value=value.agg_value,
                    session=session,
                )
            if value.agg_value == current_agg_value:
                # update the existing KPI value
                value_updated = True
                value.kpi_value = kpi.get_value(
                    agg_kind=agg_kind,
                    start_ts=timestamps.start,
                    stop_ts=timestamps.stop,
                    session=session,
                )
                Persister.update_kpi_value(
                    kpi_id=kpi.unique_id,
                    agg_kind=agg_kind,
                    agg_value=value.agg_value,
                    kpi_value=value.kpi_value,
                    session=session,
                )
        if not value_updated:
            # create a new KPI value since there is no existing one
            value = Value(
                agg_value=current_agg_value,
                kpi_value=kpi.get_value(
                    agg_kind=agg_kind,
                    start_ts=timestamps.start,
                    stop_ts=timestamps.stop,
                    session=session,
                ),
            )
            Persister.add_kpi_value(
                kpi_id=kpi.unique_id,
                agg_kind=agg_kind,
                agg_value=value.agg_value,
                kpi_value=value.kpi_value,
                session=session,
            )

    def restore_from_db(self, session: Session) -> None:
        """Restore data from database, typically after a process restart"""

        # retrieve last known period from DB
        last_period = Persister.get_last_period(session)

        # if there is no last period, nothing to do
        if not last_period:
            return

        # create/update KPIs values for all aggregation kinds which are updated once
        # per hour (D, W, M)
        if last_period != self.current_period:
            for kpi in self.kpis:
                for agg_kind in [AggKind.DAY, AggKind.WEEK, AggKind.MONTH]:
                    Processor.compute_kpi_values_for_aggregation_kind(
                        now=last_period, kpi=kpi, agg_kind=agg_kind, session=session
                    )

        # create/update KPIs values for yearly aggregations
        # which are updated only once per day
        last_period_day = last_period.get_truncated_value(AggKind.DAY)
        if self.current_day != last_period_day:
            for kpi in self.kpis:
                Processor.compute_kpi_values_for_aggregation_kind(
                    now=last_period, kpi=kpi, agg_kind=AggKind.YEAR, session=session
                )
