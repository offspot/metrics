from datetime import datetime

import pytest
import sqlalchemy as sa

from backend.business.indicators.processor import Processor
from backend.db import Session
from backend.db.models import IndicatorPeriod


@pytest.mark.parametrize(
    "init_iso_datetime, next_iso_datetime, has_changed, expected_year, expected_month,"
    " expected_day, expected_hour, expected_weekday",
    [
        ("2023-06-08 10:18:12", "2023-06-08 10:58:31", False, 2023, 6, 8, 10, 4),
        ("2023-06-08 10:18:12", "2023-06-08 11:00:31", True, 2023, 6, 8, 10, 4),
        ("2022-06-08 10:18:12", "2022-06-09 09:00:31", True, 2022, 6, 8, 10, 3),
        ("2023-06-08 11:19:12", "2023-06-09 09:00:31", True, 2023, 6, 8, 11, 4),
    ],
)
def test_periods(
    init_iso_datetime: str,
    next_iso_datetime: str,
    has_changed: bool,
    expected_year: int,
    expected_month: int,
    expected_day: int,
    expected_hour: int,
    expected_weekday: int,
) -> None:
    processor = Processor(datetime.fromisoformat(init_iso_datetime))
    init_period = processor.current_period
    processor.process_tick(datetime.fromisoformat(next_iso_datetime))
    next_period = processor.current_period
    assert (init_period != next_period) == has_changed
    with Session.begin() as session:
        dbPeriod = session.execute(
            sa.select(IndicatorPeriod)
            .where(IndicatorPeriod.year == init_period.year)
            .where(IndicatorPeriod.month == init_period.month)
            .where(IndicatorPeriod.day == init_period.day)
            .where(IndicatorPeriod.hour == init_period.hour)
        ).scalar_one_or_none()
        assert dbPeriod
        assert dbPeriod.year == expected_year
        assert dbPeriod.month == expected_month
        assert dbPeriod.day == expected_day
        assert dbPeriod.hour == expected_hour
        assert dbPeriod.weekday == expected_weekday
