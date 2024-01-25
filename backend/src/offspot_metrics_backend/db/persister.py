import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.kpis.value import Value
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.models import IndicatorDimension as DimensionDb
from offspot_metrics_backend.db.models import IndicatorPeriod as PeriodDb
from offspot_metrics_backend.db.models import IndicatorRecord as RecordDb
from offspot_metrics_backend.db.models import IndicatorState as StateDb
from offspot_metrics_backend.db.models import KpiRecord, KpiValue


class Persister:
    @classmethod
    def clear_indicator_states(cls, session: Session) -> None:
        """Delete all indicator states stored in DB"""
        session.execute(sa.delete(StateDb))

    @classmethod
    def persist_period(cls, period: Period, session: Session) -> PeriodDb:
        """Store one period in DB in DB if not already present"""
        db_period = PeriodDb.get_or_none(period, session)

        if not db_period:
            db_period = PeriodDb.from_period(period)
            session.add(db_period)

        return db_period

    @classmethod
    def persist_indicator_dimensions(
        cls, indicators: list[Indicator], session: Session
    ) -> None:
        """Store all dimensions of all indicators in DB if not already present"""
        for indicator in indicators:
            for record in indicator.get_records():
                db_dimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one_or_none()

                if not db_dimension:
                    db_dimension = DimensionDb(
                        record.dimensions.value0,
                        record.dimensions.value1,
                        record.dimensions.value2,
                    )
                    session.add(db_dimension)

    @classmethod
    def persist_indicator_records(
        cls, period: PeriodDb, indicators: list[Indicator], session: Session
    ) -> None:
        """Store all indicator records in DB"""
        for indicator in indicators:
            for record in indicator.get_records():
                db_dimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one()
                db_record = RecordDb(indicator.unique_id, record.value)
                db_record.dimension = db_dimension
                db_record.period = period
                session.add(db_record)

    @classmethod
    def persist_indicator_states(
        cls, period: PeriodDb, indicators: list[Indicator], session: Session
    ) -> None:
        """Store all indicators temporary state in DB"""
        for indicator in indicators:
            for state in indicator.get_states():
                db_dimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == state.dimensions.value0)
                    .where(DimensionDb.value1 == state.dimensions.value1)
                    .where(DimensionDb.value2 == state.dimensions.value2)
                ).scalar_one()
                db_state = StateDb(indicator.unique_id, state.value)
                db_state.dimension = db_dimension
                db_state.period = period
                session.add(db_state)

    @classmethod
    def get_last_period(cls, session: Session) -> Period | None:
        """Return the last period stored in DB"""
        db_period = session.execute(
            sa.select(PeriodDb).order_by(PeriodDb.timestamp.desc()).limit(1)
        ).scalar_one_or_none()
        if not db_period:
            return None
        return db_period.to_period()

    @classmethod
    def get_restore_data(
        cls, period: Period, indicator_id: int, session: Session
    ) -> list[StateDb]:
        """Return all state data to restore from DB to memory"""
        return list(
            session.execute(
                sa.select(StateDb)
                .where(StateDb.indicator_id == indicator_id)
                .join(PeriodDb)
                .where(PeriodDb.timestamp == period.timestamp)
            ).scalars()
        )

    @classmethod
    def has_indicator_records_for_period(cls, period: Period, session: Session) -> bool:
        """Checks if we have indicator records for a given period"""
        return (
            session.query(RecordDb)
            .join(PeriodDb)
            .where(PeriodDb.timestamp == period.timestamp)
            .count()
            > 0
        )

    @classmethod
    def get_kpi_values(
        cls,
        kpi_id: int,
        agg_kind: AggKind,
        session: Session,
    ) -> list[Value]:
        """Return all KPI values for a given KPI and a given kind of period"""
        return [
            Value(agg_value=dbValue.agg_value, kpi_value=dbValue.kpi_value)
            for dbValue in session.execute(
                sa.select(KpiRecord)
                .where(KpiRecord.kpi_id == kpi_id)
                .where(KpiRecord.agg_kind == agg_kind.value)
            ).scalars()
        ]

    @classmethod
    def delete_kpi_value(
        cls, kpi_id: int, agg_kind: AggKind, agg_value: str, session: Session
    ) -> None:
        """Delete a KPI value for a given KPI, kind of period and period"""
        session.execute(
            sa.delete(KpiRecord)
            .where(KpiRecord.kpi_id == kpi_id)
            .where(KpiRecord.agg_kind == agg_kind.value)
            .where(KpiRecord.agg_value == agg_value)
        )

    @classmethod
    def update_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: AggKind,
        agg_value: str,
        kpi_value: KpiValue,
        session: Session,
    ) -> None:
        """Update a KPI value for a given KPI, kind of period and period"""
        obj = session.execute(
            sa.select(KpiRecord)
            .where(KpiRecord.kpi_id == kpi_id)
            .where(KpiRecord.agg_kind == agg_kind.value)
            .where(KpiRecord.agg_value == agg_value)
        ).scalar_one()
        obj.kpi_value = kpi_value

    @classmethod
    def add_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: AggKind,
        agg_value: str,
        kpi_value: KpiValue,
        session: Session,
    ) -> None:
        """Add a KPI value for a given KPI, kind of period and period"""
        session.add(
            KpiRecord(
                kpi_id=kpi_id,
                agg_kind=agg_kind.value,
                agg_value=agg_value,
                kpi_value=kpi_value,
            )
        )

    @classmethod
    def cleanup_obsolete_data(cls, current_period: Period, session: Session) -> None:
        """Delete obsolete data from DB

        For now, obsolete data is indicators older than 1 year compared to current
        period. Associated unused data (records, states, dimensions) is cleaned as
        well.
        """

        oldest_valid_ts = current_period.get_shifted(relativedelta(years=-1)).timestamp

        # delete records associated with old periods
        # we use the PeriodDb table to use its index for efficient query, even if the
        # information is already present in RecordDb
        session.execute(
            sa.delete(RecordDb).where(
                RecordDb.period_id.in_(
                    sa.select(PeriodDb.timestamp).where(
                        PeriodDb.timestamp < oldest_valid_ts
                    )
                )
            )
        )

        # just in case, delete old states associated with old periods (should never
        # be needed, but will avoid DB integrity errors)
        # we use the PeriodDb table to use its index for efficient query, even if the
        # information is already present in StateDb
        session.execute(
            sa.delete(StateDb).where(
                StateDb.period_id.in_(
                    sa.select(PeriodDb.timestamp).where(
                        PeriodDb.timestamp < oldest_valid_ts
                    )
                )
            )
        )

        # delete old periods
        session.execute(sa.delete(PeriodDb).where(PeriodDb.timestamp < oldest_valid_ts))

        # delete indicator dimensions that are not used anymore
        session.execute(
            sa.delete(DimensionDb).where(
                DimensionDb.id.not_in(sa.select(RecordDb.dimension_id).distinct())
            )
        )
