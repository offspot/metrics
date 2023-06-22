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


class TooManyDimensions(Exception):
    """Raised when an indicator has too many dimensions, not suppported in storage"""

    pass


class Persister:
    @classmethod
    def clear_indicator_states(cls, session: Session) -> None:
        session.execute(sa.delete(StateDb))

    @classmethod
    def persist_period(cls, period: PeriodBiz, session: Session) -> PeriodDb:
        dbPeriod = PeriodDb.get_from_db_or_none(period, session)

        if not dbPeriod:
            dbPeriod = PeriodDb.from_period(period)
            session.add(dbPeriod)

        return dbPeriod

    @classmethod
    def persist_indicator_dimensions(
        cls, indicators: List[Indicator], session: Session
    ) -> None:
        for indicator in indicators:
            for record in indicator.get_records():
                nb_dimensions = len(record.dimensions)
                if nb_dimensions > 3:
                    raise TooManyDimensions()

                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.get_dimension_value(0))
                    .where(DimensionDb.value1 == record.get_dimension_value(1))
                    .where(DimensionDb.value2 == record.get_dimension_value(2))
                ).scalar_one_or_none()

                if not dbDimension:
                    dbDimension = DimensionDb(
                        record.get_dimension_value(0),
                        record.get_dimension_value(1),
                        record.get_dimension_value(2),
                    )
                    session.add(dbDimension)

    @classmethod
    def persist_indicator_records(
        cls, period: PeriodDb, indicators: List[Indicator], session: Session
    ) -> None:
        for indicator in indicators:
            for record in indicator.get_records():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.get_dimension_value(0))
                    .where(DimensionDb.value1 == record.get_dimension_value(1))
                    .where(DimensionDb.value2 == record.get_dimension_value(2))
                ).scalar_one()
                dbRecord = RecordDb(indicator.unique_id, record.value)
                dbRecord.dimension = dbDimension
                dbRecord.period = period
                session.add(dbRecord)

    @classmethod
    def persist_indicator_states(
        cls, period: PeriodDb, indicators: List[Indicator], session: Session
    ) -> None:
        for indicator in indicators:
            for state in indicator.get_states():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == state.get_dimension_value(0))
                    .where(DimensionDb.value1 == state.get_dimension_value(1))
                    .where(DimensionDb.value2 == state.get_dimension_value(2))
                ).scalar_one()
                dbState = StateDb(indicator.unique_id, state.value)
                dbState.dimension = dbDimension
                dbState.period = period
                session.add(dbState)

    @classmethod
    def get_last_current_period(cls, session: Session) -> Optional[PeriodBiz]:
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
        cls, kpi_id: int, kind: str, session: Session
    ) -> List[KpiValueBiz]:
        return [
            KpiValueBiz(period=dbValue.period, value=dbValue.value)
            for dbValue in list(
                session.execute(
                    sa.select(KpiValueDb)
                    .where(KpiValueDb.kpi_id == kpi_id)
                    .where(KpiValueDb.kind == kind)
                ).scalars()
            )
        ]

    @classmethod
    def delete_kpi_value(
        cls, kpi_id: int, kind: str, period: str, session: Session
    ) -> None:
        session.execute(
            sa.delete(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.kind == kind)
            .where(KpiValueDb.period == period)
        )

    @classmethod
    def update_kpi_value(
        cls, kpi_id: int, kind: str, period: str, value: str, session: Session
    ) -> None:
        obj = session.execute(
            sa.select(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.kind == kind)
            .where(KpiValueDb.period == period)
        ).scalar_one()
        obj.value = value

    @classmethod
    def add_kpi_value(
        cls, kpi_id: int, kind: str, period: str, value: str, session: Session
    ) -> None:
        session.add(KpiValueDb(kpi_id=kpi_id, kind=kind, period=period, value=value))

    @classmethod
    def cleanup_old_stuff(cls, now: PeriodBiz, session: Session) -> None:
        min_ts = (now.get_datetime() - relativedelta(years=1)).timestamp()

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
