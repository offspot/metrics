from datetime import datetime

import pytest
from backend.business.indicators.indicator import Indicator
from backend.business.indicators.processor import Processor
from backend.business.inputs.input import Input
from backend.business.period import Period
from backend.db.models import IndicatorPeriod
from sqlalchemy.orm import Session


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
    input1: Input,
    total_indicator: Indicator,
    dbsession: Session,
) -> None:
    processor = Processor(Period(datetime.fromisoformat(init_iso_datetime)))
    processor.indicators = [total_indicator]
    processor.process_input(input1)
    init_period = processor.current_period
    processor.process_tick(
        Period(datetime.fromisoformat(next_iso_datetime)),
        dbsession,
    )
    next_period = processor.current_period
    assert (init_period != next_period) == has_changed
    dbPeriod = IndicatorPeriod.get_from_db_or_none(init_period, dbsession)
    assert dbPeriod
    assert dbPeriod.year == expected_year
    assert dbPeriod.month == expected_month
    assert dbPeriod.day == expected_day
    assert dbPeriod.hour == expected_hour
    assert dbPeriod.weekday == expected_weekday


@pytest.mark.parametrize(
    "curdate,kind,expected",
    [
        ("2023-06-08 10:18:12", "Y", "2023"),
        ("2023-06-08 10:18:12", "M", "2023-06"),
        ("2023-06-08 10:18:12", "W", "2023 W23"),
        ("2023-06-08 10:18:12", "D", "2023-06-08"),
    ],
)
def test_truncated_value(curdate: str, kind: str, expected: str) -> None:
    assert Period(datetime.fromisoformat(curdate)).get_truncated_value(kind) == expected


def test_truncated_value_wrong_kind() -> None:
    with pytest.raises(AttributeError):
        Period(datetime.now()).get_truncated_value("Q")
