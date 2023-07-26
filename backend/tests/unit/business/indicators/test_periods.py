from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.processor import Processor
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db.models import IndicatorPeriod


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
    assert (init_period != processor.current_period) == has_changed
    dbPeriod = IndicatorPeriod.get_or_none(init_period, dbsession)
    assert dbPeriod
    period = Period.from_timestamp(dbPeriod.timestamp)
    assert period.year == expected_year
    assert period.month == expected_month
    assert period.day == expected_day
    assert period.hour == expected_hour
    assert period.weekday == expected_weekday


@pytest.mark.parametrize(
    "curdate,kind,expected",
    [
        ("2023-06-08 10:18:12", AggKind.YEAR, "2023"),
        ("2023-06-08 10:18:12", AggKind.MONTH, "2023-06"),
        ("2023-06-08 10:18:12", AggKind.WEEK, "2023 W23"),
        ("2023-06-08 10:18:12", AggKind.DAY, "2023-06-08"),
    ],
)
def test_truncated_value(curdate: str, kind: AggKind, expected: str) -> None:
    assert Period(datetime.fromisoformat(curdate)).get_truncated_value(kind) == expected
