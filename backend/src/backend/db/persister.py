from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Session

from backend.business.indicators.indicator import Indicator
from backend.business.indicators.period import Period as PeriodBiz
from backend.db.models import IndicatorDimension as DimensionDb
from backend.db.models import IndicatorPeriod as PeriodDb
from backend.db.models import IndicatorRecord as RecordDb


class TooManyDimensions(Exception):
    """Raised when an indicator has too many dimensions, not suppported in storage"""

    pass


class Persister:
    @classmethod
    def persist_indicators(
        cls, period: PeriodBiz, indicators: List[Indicator], session: Session
    ) -> None:
        dbPeriod = session.execute(
            sa.select(PeriodDb)
            .where(PeriodDb.year == period.year)
            .where(PeriodDb.month == period.month)
            .where(PeriodDb.day == period.day)
            .where(PeriodDb.hour == period.hour)
        ).scalar_one_or_none()

        if not dbPeriod:
            dbPeriod = PeriodDb(
                period.year,
                period.month,
                period.day,
                period.weekday,
                period.hour,
            )
            session.add(dbPeriod)

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

                dbRecord = RecordDb(indicator.unique_id, record.value)
                dbRecord.dimension = dbDimension
                dbRecord.period = dbPeriod
                session.add(dbRecord)
