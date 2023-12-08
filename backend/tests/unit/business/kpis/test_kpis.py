from collections.abc import Callable
from datetime import datetime, timedelta
from typing import cast

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from tests.unit.conftest import DummyKpiValue

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis import get_kpi_name
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.processor import Processor
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db import count_from_stmt
from offspot_metrics_backend.db.models import IndicatorPeriod as PeriodDb
from offspot_metrics_backend.db.models import KpiRecord, KpiValue


@pytest.fixture
def get_dummy_value() -> Callable[[str], DummyKpiValue]:
    def func(value: str) -> DummyKpiValue:
        return DummyKpiValue(root=value)

    return func


@pytest.fixture
def init_datetime_day_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1686182400 - 1686268800")


@pytest.fixture
def init_datetime_day_minus_one_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1686096000 - 1686182400")


@pytest.fixture
def init_datetime_day_plus_one_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1686268800 - 1686355200")


@pytest.fixture
def init_datetime_day_plus_two_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1686355200 - 1686441600")


@pytest.fixture
def init_datetime_day_plus_three_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1686787200 - 1686873600")


@pytest.fixture
def init_datetime_week_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("W - 1685923200 - 1686528000")


@pytest.fixture
def init_datetime_week_plus_one_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("W - 1686528000 - 1687132800")


@pytest.fixture
def init_datetime_month_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("M - 1685577600 - 1688169600")


@pytest.fixture
def init_datetime_year_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("Y - 1672531200 - 1704067200")


@pytest.fixture
def previous_datetime_day_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("D - 1672704000 - 1672790400")


@pytest.fixture
def previous_datetime_week_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("W - 1672617600 - 1673222400")


@pytest.fixture
def previous_datetime_month_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("M - 1672531200 - 1675209600")


@pytest.fixture
def previous_datetime_year_dummyvalue(
    get_dummy_value: Callable[[str], DummyKpiValue]
) -> DummyKpiValue:
    return get_dummy_value("Y - 1672531200 - 1704067200")


@pytest.mark.parametrize(
    "agg_kind, now, expected_start_ts, expected_end_ts",
    [
        (AggKind.DAY, "2023-06-08 10:58:31", 1686182400, 1686268800),
        (AggKind.DAY, "2023-01-31 01:18:31", 1675123200, 1675209600),
        (AggKind.WEEK, "2023-01-01 01:18:31", 1672012800, 1672617600),
        (AggKind.WEEK, "2023-01-31 01:18:31", 1675036800, 1675641600),
        (AggKind.MONTH, "2023-01-01 01:18:31", 1672531200, 1675209600),
        (AggKind.MONTH, "2023-12-01 01:18:31", 1701388800, 1704067200),
        (AggKind.YEAR, "2023-01-01 01:18:31", 1672531200, 1704067200),
        (AggKind.YEAR, "2024-02-29 01:18:31", 1704067200, 1735689600),
    ],
)
def test_timestamps(
    agg_kind: AggKind,
    now: str,
    expected_start_ts: int,
    expected_end_ts: int,
) -> None:
    res = Period(datetime.fromisoformat(now)).get_interval(agg_kind=agg_kind)
    assert res.start == expected_start_ts
    assert res.stop == expected_end_ts


@pytest.mark.parametrize(
    "agg_kind, now, expected_periods",
    [
        (
            AggKind.DAY,
            "2023-01-03 10:58:31",
            [f"2022-12-{i:02}" for i in range(28, 32)]
            + [f"2023-01-{i:02}" for i in range(1, 4)],
        ),
        (
            AggKind.WEEK,
            "2023-01-03 01:18:31",
            [f"2022 W{i:02}" for i in range(50, 53)] + ["2023 W01"],
        ),
        (
            AggKind.MONTH,
            "2023-01-03 01:18:31",
            [f"2022-{i:02}" for i in range(2, 13)] + ["2023-01"],
        ),
        (AggKind.YEAR, "2023-01-01 01:18:31", None),
    ],
)
def test_get_aggregations_to_keep(
    agg_kind: AggKind,
    now: str,
    expected_periods: list[str] | None,
) -> None:
    res = Processor.get_aggregations_to_keep(
        agg_kind=agg_kind, now=Period(datetime.fromisoformat(now))
    )
    if not expected_periods:
        assert res is None
    else:
        assert res is not None
        assert sorted(res) == sorted(expected_periods)


def get_kpi_values(dbsession: Session):
    def get_dummy_key(value: KpiValue) -> DummyKpiValue:
        return cast(DummyKpiValue, value)

    return sorted(
        dbsession.execute(select(KpiRecord.kpi_value)).scalars(), key=get_dummy_key
    )


def test_process_tick(
    init_datetime_day_dummyvalue: DummyKpiValue,
    init_datetime_week_dummyvalue: DummyKpiValue,
    init_datetime_month_dummyvalue: DummyKpiValue,
    init_datetime_year_dummyvalue: DummyKpiValue,
    init_datetime_day_plus_one_dummyvalue: DummyKpiValue,
    init_datetime_day_plus_two_dummyvalue: DummyKpiValue,
    init_datetime_day_plus_three_dummyvalue: DummyKpiValue,
    init_datetime_week_plus_one_dummyvalue: DummyKpiValue,
    processor: Processor,
    dummy_kpi: Kpi,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiRecord))
    processor.process_tick(tick_period=Period(init_datetime), session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 0
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(minutes=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 0
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(hours=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 3
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(hours=4)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 3
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 4
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=1) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 5
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_day_plus_one_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=2)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 5
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_day_plus_one_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=2) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 6
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_day_plus_one_dummyvalue,
            init_datetime_day_plus_two_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=7)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 6
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_day_plus_one_dummyvalue,
            init_datetime_day_plus_two_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=7) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiRecord)) == 7
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_plus_one_dummyvalue,
            init_datetime_day_plus_two_dummyvalue,
            init_datetime_day_plus_three_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_week_plus_one_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )


def test_restore_kpis_from_almost_empty_db(
    init_datetime_week_dummyvalue: DummyKpiValue,
    init_datetime_month_dummyvalue: DummyKpiValue,
    init_datetime_year_dummyvalue: DummyKpiValue,
    init_datetime_day_minus_one_dummyvalue: DummyKpiValue,
    processor: Processor,
    dummy_kpi: Kpi,
    init_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiRecord))
    dbsession.execute(delete(PeriodDb))

    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 0

    init_period = PeriodDb.from_datetime(init_datetime)
    dbsession.add(init_period)
    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 0
    dbsession.delete(init_period)

    minus_1_hour = PeriodDb.from_datetime(init_datetime - timedelta(hours=1))
    dbsession.add(minus_1_hour)
    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 3
    dbsession.delete(minus_1_hour)

    minus_1_day = PeriodDb.from_datetime(init_datetime - timedelta(days=1))
    dbsession.add(minus_1_day)
    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 4
    assert get_kpi_values(dbsession) == sorted(
        [
            init_datetime_day_minus_one_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )


def test_restore_kpis_from_filled_db(
    get_dummy_value: Callable[[str], DummyKpiValue],
    previous_datetime_day_dummyvalue: DummyKpiValue,
    previous_datetime_week_dummyvalue: DummyKpiValue,
    previous_datetime_month_dummyvalue: DummyKpiValue,
    previous_datetime_year_dummyvalue: DummyKpiValue,
    processor: Processor,
    dummy_kpi: Kpi,
    previous_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiRecord))
    dbsession.execute(delete(PeriodDb))

    dbsession.add(
        KpiRecord(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.YEAR.value,
            agg_value="2023",
            kpi_value=get_dummy_value("whatever"),
        )
    )

    dbsession.add(
        KpiRecord(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.MONTH.value,
            agg_value="2023-01",
            kpi_value=get_dummy_value("whatever"),
        )
    )
    dbsession.add(
        KpiRecord(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.WEEK.value,
            agg_value="2023 W01",
            kpi_value=get_dummy_value("whatever"),
        )
    )
    dbsession.add(
        KpiRecord(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.DAY.value,
            agg_value="2023-01-03",
            kpi_value=get_dummy_value("whatever"),
        )
    )

    dbsession.add(PeriodDb.from_datetime(previous_datetime))

    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiRecord)) == 4
    assert get_kpi_values(dbsession) == sorted(
        [
            previous_datetime_day_dummyvalue,
            previous_datetime_week_dummyvalue,
            previous_datetime_month_dummyvalue,
            previous_datetime_year_dummyvalue,
        ]
    )


@pytest.mark.parametrize(
    "kpi_id, expected_name",
    [
        (2001, "PackagePopularity"),
        (2003, "TotalUsage"),
        (2004, "Uptime"),
        (2005, "SharedFiles"),
    ],
)
def test_kpi_names(kpi_id: int, expected_name: str):
    assert expected_name == get_kpi_name(kpi_id)


def test_kpi_names_error():
    with pytest.raises(ValueError):
        get_kpi_name(1001)
