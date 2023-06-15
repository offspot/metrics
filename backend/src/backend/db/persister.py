from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from backend.business.indicators.indicator import Indicator
from backend.business.period import Period as PeriodBiz
from backend.db.models import IndicatorDimension as DimensionDb
from backend.db.models import IndicatorPeriod as PeriodDb
from backend.db.models import IndicatorRecord as RecordDb
from backend.db.models import IndicatorState as StateDb


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
    def get_last_current_period(cls, session: Session) -> Optional[PeriodDb]:
        dbPeriod = session.execute(
            sa.select(PeriodDb)
            .order_by(PeriodDb.year.desc())
            .order_by(PeriodDb.month.desc())
            .order_by(PeriodDb.day.desc())
            .order_by(PeriodDb.hour.desc())
            .limit(1)
        ).scalar_one_or_none()
        return dbPeriod

    @classmethod
    def get_restore_data(
        cls, period: PeriodDb, indicator_id: int, session: Session
    ) -> List[StateDb]:
        dbPeriod = session.execute(
            sa.select(StateDb)
            .where(StateDb.indicator_id == indicator_id)
            .where(StateDb.period_id == period.id)
        ).scalars()
        return list(dbPeriod)
