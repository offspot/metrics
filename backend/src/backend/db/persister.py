from typing import List, Optional

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from backend.business.indicators.indicator import Indicator
from backend.business.kpis.value import Value as KpiValueBiz
from backend.business.period import Period as PeriodBiz
from backend.db.models import IndicatorDimension as DimensionDb
from backend.db.models import IndicatorPeriod as PeriodDb
from backend.db.models import IndicatorRecord as RecordDb
from backend.db.models import IndicatorState as StateDb
from backend.db.models import KpiValue as KpiValueDb


class Persister:
    @classmethod
    def clear_indicator_states(cls, session: Session) -> None:
        """Delete all indicator states stored in DB"""
        session.execute(sa.delete(StateDb))

    @classmethod
    def persist_period(cls, period: PeriodBiz, session: Session) -> PeriodDb:
        """Store one period in DB in DB if not already present"""
        dbPeriod = PeriodDb.get_or_none(period, session)

        if not dbPeriod:
            dbPeriod = PeriodDb.from_period(period)
            session.add(dbPeriod)

        return dbPeriod

    @classmethod
    def persist_indicator_dimensions(
        cls, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all dimensions of all indicators in DB if not already present"""
        for indicator in indicators:
            for record in indicator.get_records():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one_or_none()

                if not dbDimension:
                    dbDimension = DimensionDb(
                        record.dimensions.value0,
                        record.dimensions.value1,
                        record.dimensions.value2,
                    )
                    session.add(dbDimension)

    @classmethod
    def persist_indicator_records(
        cls, period: PeriodDb, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all indicator records in DB"""
        for indicator in indicators:
            for record in indicator.get_records():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one()
                dbRecord = RecordDb(indicator.unique_id, record.value)
                dbRecord.dimension = dbDimension
                dbRecord.period = period
                session.add(dbRecord)

    @classmethod
    def persist_indicator_states(
        cls, period: PeriodDb, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all indicators temporary state in DB"""
        for indicator in indicators:
            for state in indicator.get_states():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == state.dimensions.value0)
                    .where(DimensionDb.value1 == state.dimensions.value1)
                    .where(DimensionDb.value2 == state.dimensions.value2)
                ).scalar_one()
                dbState = StateDb(indicator.unique_id, state.value)
                dbState.dimension = dbDimension
                dbState.period = period
                session.add(dbState)

    @classmethod
    def get_last_current_period(cls, session: Session) -> Optional[PeriodBiz]:
        """Return the last period stored in DB"""
        dbPeriod = session.execute(
            sa.select(PeriodDb)
            .order_by(PeriodDb.year.desc())
            .order_by(PeriodDb.month.desc())
            .order_by(PeriodDb.day.desc())
            .order_by(PeriodDb.hour.desc())
            .limit(1)
        ).scalar_one_or_none()
        if not dbPeriod:
            return None
        return dbPeriod.to_period()

    @classmethod
    def get_restore_data(
        cls, period: PeriodBiz, indicator_id: int, session: Session
    ) -> List[StateDb]:
        """Return all state data to restore from DB to memory"""
        return list(
            session.execute(
                sa.select(StateDb)
                .where(StateDb.indicator_id == indicator_id)
                .join(PeriodDb)
                .where(PeriodDb.year == period.year)
                .where(PeriodDb.month == period.month)
                .where(PeriodDb.day == period.day)
                .where(PeriodDb.hour == period.hour)
            ).scalars()
        )

    @classmethod
    def get_kpi_values(
        cls, kpi_id: int, agg_kind: str, session: Session
    ) -> List[KpiValueBiz]:
        """Return all KPI values for a given KPI and a given kind of period"""
        return [
            KpiValueBiz(agg_value=dbValue.agg_value, kpi_value=dbValue.kpi_value)
            for dbValue in list(
                session.execute(
                    sa.select(KpiValueDb)
                    .where(KpiValueDb.kpi_id == kpi_id)
                    .where(KpiValueDb.agg_kind == agg_kind)
                ).scalars()
            )
        ]

    @classmethod
    def delete_kpi_value(
        cls, kpi_id: int, agg_kind: str, agg_value: str, session: Session
    ) -> None:
        """Delete a KPI value for a given KPI, kind of period and period"""
        session.execute(
            sa.delete(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.agg_kind == agg_kind)
            .where(KpiValueDb.agg_value == agg_value)
        )

    @classmethod
    def update_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: str,
        agg_value: str,
        kpi_value: str,
        session: Session,
    ) -> None:
        """Update a KPI value for a given KPI, kind of period and period"""
        obj = session.execute(
            sa.select(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.agg_kind == agg_kind)
            .where(KpiValueDb.agg_value == agg_value)
        ).scalar_one()
        obj.kpi_value = kpi_value

    @classmethod
    def add_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: str,
        agg_value: str,
        kpi_value: str,
        session: Session,
    ) -> None:
        """Add a KPI value for a given KPI, kind of period and period"""
        session.add(
            KpiValueDb(
                kpi_id=kpi_id,
                agg_kind=agg_kind,
                agg_value=agg_value,
                kpi_value=kpi_value,
            )
        )

    @classmethod
    def cleanup_old_stuff(cls, current_period: PeriodBiz, session: Session) -> None:
        """Delete old stuff from DB

        For now, olf stuff is indicators older than 1 year compared to current_period.
        Unused associated data (records, states, dimensions) are cleaned as well.
        """

        min_ts = current_period.get_shifted(relativedelta(years=-1)).timestamp

        # delete records associated with old periods
        session.execute(
            sa.delete(RecordDb).where(
                RecordDb.period_id.in_(
                    sa.select(PeriodDb.id).where(PeriodDb.timestamp < min_ts)
                )
            )
        )

        # just in case, delete old states associated with old periods (should never
        # be needed, but will avoid DB integrity errors)
        session.execute(
            sa.delete(StateDb).where(
                StateDb.period_id.in_(
                    sa.select(PeriodDb.id).where(PeriodDb.timestamp < min_ts)
                )
            )
        )

        # delete old periods
        session.execute(sa.delete(PeriodDb).where(PeriodDb.timestamp < min_ts))

        # delete indicator dimensions that are not used anymore
        session.execute(
            sa.delete(DimensionDb).where(
                DimensionDb.id.not_in(sa.select(RecordDb.dimension_id).distinct())
            )
        )
