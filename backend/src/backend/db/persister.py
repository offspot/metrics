from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio.session import AsyncSession

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
    async def persist_indicators(
        cls, period: PeriodBiz, indicators: List[Indicator], session: AsyncSession
    ) -> None:
        dbPeriod = (
            await session.execute(
                sa.select(PeriodDb)
                .where(PeriodDb.year == period.year)
                .where(PeriodDb.month == period.month)
                .where(PeriodDb.day == period.day)
                .where(PeriodDb.hour == period.hour)
            )
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

                dbDimension = (
                    await session.execute(
                        sa.select(DimensionDb)
                        .where(DimensionDb.value0 == record.get_dimension_value(0))
                        .where(DimensionDb.value1 == record.get_dimension_value(1))
                        .where(DimensionDb.value2 == record.get_dimension_value(2))
                    )
                ).scalar_one_or_none()

                if not dbDimension:
                    # sa.literal is usefull only due to a SQLAlchemy/mypy issue
                    # see https://github.com/sqlalchemy/sqlalchemy/issues/9919
                    dbDimension = DimensionDb(
                        sa.literal(record.get_dimension_value(0)),
                        sa.literal(record.get_dimension_value(1)),
                        sa.literal(record.get_dimension_value(2)),
                    )
                    session.add(dbDimension)

                dbRecord = RecordDb(indicator.unique_id, record.value)
                dbRecord.dimension = dbDimension
                dbRecord.period = dbPeriod
                session.add(dbRecord)
