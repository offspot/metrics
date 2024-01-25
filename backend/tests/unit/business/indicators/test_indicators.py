from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.indicators import get_indicator_name
from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.holder import Record
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.processor import Processor
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db import count_from_stmt
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
    IndicatorState,
)


def test_no_input(processor: Processor, total_indicator: Indicator) -> None:
    processor.indicators.append(total_indicator)
    assert len(list(total_indicator.get_records())) == 0


def test_one_input(
    processor: Processor,
    input1: Input,
    total_indicator: Indicator,
    failing_indicator: Indicator,
) -> None:
    processor.indicators = [failing_indicator, total_indicator, failing_indicator]
    processor.process_input(input1)
    assert list(total_indicator.get_records()) == [
        Record(value=1, dimensions=DimensionsValues(None, None, None)),
    ]


def test_one_input_repeated(
    processor: Processor, input1: Input, total_indicator: Indicator
) -> None:
    processor.indicators = [total_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    assert list(total_indicator.get_records()) == [
        Record(value=2, dimensions=DimensionsValues(None, None, None)),
    ]


def test_another_input(
    processor: Processor, total_indicator: Indicator, another_input: Input
) -> None:
    processor.indicators = [total_indicator]
    processor.process_input(another_input)
    assert len(list(total_indicator.get_records())) == 0


def test_total_by_content(
    processor: Processor,
    input1: Input,
    input2: Input,
    input3: Input,
    another_input: Input,
    total_by_content_indicator: Indicator,
) -> None:
    processor.indicators = [total_by_content_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    assert list(total_by_content_indicator.get_records()) == [
        Record(value=3, dimensions=DimensionsValues("content1", None, None)),
        Record(value=1, dimensions=DimensionsValues("content2", None, None)),
    ]


def test_total_by_content_and_subfolder(
    processor: Processor,
    input1: Input,
    input2: Input,
    input3: Input,
    another_input: Input,
    total_by_content_and_subfolder_indicator: Indicator,
) -> None:
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    assert list(total_by_content_and_subfolder_indicator.get_records()) == [
        Record(value=2, dimensions=DimensionsValues("content1", "subfolder1", None)),
        Record(value=1, dimensions=DimensionsValues("content1", "subfolder2", None)),
        Record(value=1, dimensions=DimensionsValues("content2", "subfolder1", None)),
    ]


def test_process_tick(
    processor: Processor,
    input1: Input,
    input2: Input,
    input3: Input,
    another_input: Input,
    total_by_content_and_subfolder_indicator: Indicator,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_tick(Period(init_datetime), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 0
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 0
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    processor.process_tick(Period(init_datetime + timedelta(minutes=1)), dbsession)
    # double tick to check that this is idempotent
    processor.process_tick(Period(init_datetime + timedelta(minutes=2)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 3
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1
    processor.process_tick(Period(init_datetime + timedelta(hours=1)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 3
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_tick(
        Period(init_datetime + timedelta(hours=1, minutes=1)), dbsession
    )
    assert count_from_stmt(dbsession, select(IndicatorState)) == 2
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 3
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2
    processor.process_tick(Period(init_datetime + timedelta(hours=2)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 5
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2
    processor.post_process_tick(Period(init_datetime + timedelta(hours=2)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 5
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2
    processor.post_process_tick(
        Period(init_datetime + relativedelta(years=1)), dbsession
    )
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 5
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2
    processor.post_process_tick(
        Period(init_datetime + relativedelta(years=1) + relativedelta(days=1)),
        dbsession,
    )
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 0
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 0


def test_restore_from_db_current_period(
    processor: Processor,
    dbsession: Session,
) -> None:
    init_dt = "2020-06-01 13:00:00"
    processor.restore_from_db(dbsession)
    processor.process_tick(Period(datetime.fromisoformat(init_dt)), dbsession)
    assert processor.current_period == Period(datetime.fromisoformat(init_dt))
    datas = [
        # indicator period in DB, now datetime       , expected current datetime
        ("2021-06-01 13:00:00", "2021-06-01 13:10:00", "2021-06-01 13:00:00"),
        ("2021-06-01 14:00:00", "2021-06-01 14:10:00", "2021-06-01 14:00:00"),
        ("2021-06-02 13:00:00", "2021-06-02 13:10:00", "2021-06-02 13:00:00"),
        ("2021-07-01 13:00:00", "2021-07-01 13:10:00", "2021-07-01 13:00:00"),
        ("2022-06-01 13:00:00", "2022-06-01 13:10:00", "2022-06-01 13:00:00"),
        ("2023-06-01 13:00:00", "2023-06-01 14:10:00", "2023-06-01 14:00:00"),
    ]
    for indicator_period_in_db, now_datetime, expected_current_datetime in datas:
        dbsession.add(
            IndicatorPeriod.from_datetime(
                datetime.fromisoformat(indicator_period_in_db)
            )
        )
        processor.restore_from_db(dbsession)
        processor.process_tick(Period(datetime.fromisoformat(now_datetime)), dbsession)
        assert processor.current_period == Period(
            datetime.fromisoformat(expected_current_datetime)
        )


def test_restore_from_db_continue_same_period(
    processor: Processor,
    total_by_content_and_subfolder_indicator: Indicator,
    input1: Input,
    input2: Input,
    input3: Input,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(input3)

    processor.process_tick(Period(init_datetime + timedelta(minutes=10)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 3
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.restore_from_db(dbsession)
    processor.process_tick(Period(init_datetime + timedelta(minutes=12)), dbsession)
    assert len(total_by_content_and_subfolder_indicator.recorders) == 3
    assert count_from_stmt(dbsession, select(IndicatorState)) == 3
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.process_tick(Period(init_datetime + timedelta(hours=1)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 3
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1


def test_restore_from_db_start_new_period_not_recorded(
    processor: Processor,
    total_by_content_and_subfolder_indicator: Indicator,
    input1: Input,
    input2: Input,
    input3: Input,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(input3)

    processor.process_tick(Period(init_datetime + timedelta(minutes=10)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 3
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.restore_from_db(dbsession)
    processor.process_tick(Period(init_datetime + timedelta(days=1)), dbsession)
    assert len(total_by_content_and_subfolder_indicator.recorders) == 0
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 3
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(input3)

    processor.process_tick(
        Period(init_datetime + timedelta(days=1, hours=1)), dbsession
    )
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 6
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2


def test_restore_from_db_start_new_period_recorded(
    processor: Processor,
    total_by_content_and_subfolder_indicator: Indicator,
    input1: Input,
    input2: Input,
    input3: Input,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(input3)

    processor.process_tick(Period(init_datetime + timedelta(minutes=10)), dbsession)
    assert count_from_stmt(dbsession, select(IndicatorState)) == 3
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 0
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.process_tick(Period(init_datetime + timedelta(days=1)), dbsession)

    assert len(total_by_content_and_subfolder_indicator.recorders) == 0
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 3
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 1

    processor.restore_from_db(dbsession)

    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(input3)

    processor.process_tick(
        Period(init_datetime + timedelta(days=1, hours=1)), dbsession
    )
    assert count_from_stmt(dbsession, select(IndicatorState)) == 0
    assert count_from_stmt(dbsession, select(IndicatorRecord)) == 6
    assert count_from_stmt(dbsession, select(IndicatorDimension)) == 3
    assert count_from_stmt(dbsession, select(IndicatorPeriod)) == 2


@pytest.mark.parametrize(
    "kpi_id, expected_name",
    [
        (1001, "PackageHomeVisit"),
        (1003, "SharedFilesOperations"),
        (1004, "Uptime"),
        (1005, "TotalUsageOverall"),
        (1006, "TotalUsageByPackage"),
    ],
)
def test_indicator_names(kpi_id: int, expected_name: str):
    assert expected_name == get_indicator_name(kpi_id)


def test_indicator_names_error():
    with pytest.raises(ValueError):
        get_indicator_name(2001)
