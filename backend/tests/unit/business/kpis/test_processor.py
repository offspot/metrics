from datetime import datetime, timedelta
from typing import List

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.business.agg_kind import AggKind
from backend.business.kpis.kpi import Kpi
from backend.business.kpis.processor import Processor
from backend.business.period import Period as Period
from backend.db import count_from_stmt
from backend.db.models import IndicatorPeriod as PeriodDb
from backend.db.models import KpiValue

init_datetime_day_dummyvalue = "D - 1686182400 - 1686268800"
init_datetime_day_minus_one_dummyvalue = "D - 1686096000 - 1686182400"
init_datetime_day_plus_one_dummyvalue = "D - 1686268800 - 1686355200"
init_datetime_day_plus_two_dummyvalue = "D - 1686355200 - 1686441600"
init_datetime_day_plus_three_dummyvalue = "D - 1686787200 - 1686873600"
init_datetime_week_dummyvalue = "W - 1685923200 - 1686528000"
init_datetime_week_plus_one_dummyvalue = "W - 1686528000 - 1687132800"
init_datetime_month_dummyvalue = "M - 1685577600 - 1688169600"
init_datetime_year_dummyvalue = "Y - 1672531200 - 1704067200"

previous_datetime_day_dummyvalue = "D - 1672704000 - 1672790400"
previous_datetime_week_dummyvalue = "W - 1672617600 - 1673222400"
previous_datetime_month_dummyvalue = "M - 1672531200 - 1675209600"
previous_datetime_year_dummyvalue = "Y - 1672531200 - 1704067200"


@pytest.mark.parametrize(
    "agg_kind, now, expected_start_ts, expected_end_ts",
    [
        (AggKind.DAY, "2023-06-08 10:58:31", 1686182400, 1686268800),
        (AggKind.WEEK, "2023-01-01 01:18:31", 1672012800, 1672617600),
        (AggKind.MONTH, "2023-01-01 01:18:31", 1672531200, 1675209600),
        (AggKind.YEAR, "2023-01-01 01:18:31", 1672531200, 1704067200),
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
    expected_periods: List[str] | None,
) -> None:
    res = Processor.get_aggregations_to_keep(
        agg_kind=agg_kind, now=Period(datetime.fromisoformat(now))
    )
    if not expected_periods:
        assert res is None
    else:
        assert res is not None
        assert sorted(res) == sorted(expected_periods)


def test_process_tick(
    processor: Processor, dummy_kpi: Kpi, init_datetime: datetime, dbsession: Session
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiValue))
    processor.process_tick(tick_period=Period(init_datetime), session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 0
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(minutes=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 0
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(hours=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 3
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(hours=4)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 3
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
        [
            init_datetime_day_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
        ]
    )
    processor.process_tick(
        tick_period=Period(init_datetime + timedelta(days=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 4
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    assert count_from_stmt(dbsession, select(KpiValue)) == 5
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    assert count_from_stmt(dbsession, select(KpiValue)) == 5
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    assert count_from_stmt(dbsession, select(KpiValue)) == 6
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    assert count_from_stmt(dbsession, select(KpiValue)) == 6
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    assert count_from_stmt(dbsession, select(KpiValue)) == 7
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
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
    processor: Processor, dummy_kpi: Kpi, init_datetime: datetime, dbsession: Session
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiValue))
    dbsession.execute(delete(PeriodDb))

    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 0

    minus_1_hour = PeriodDb.from_datetime(init_datetime - timedelta(hours=1))
    dbsession.add(minus_1_hour)
    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 3
    dbsession.delete(minus_1_hour)

    minus_1_day = PeriodDb.from_datetime(init_datetime - timedelta(days=1))
    dbsession.add(minus_1_day)
    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 4
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
        [
            init_datetime_day_minus_one_dummyvalue,
            init_datetime_week_dummyvalue,
            init_datetime_month_dummyvalue,
            init_datetime_year_dummyvalue,
        ]
    )


def test_restore_kpis_from_filled_db(
    processor: Processor,
    dummy_kpi: Kpi,
    previous_datetime: datetime,
    dbsession: Session,
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiValue))
    dbsession.execute(delete(PeriodDb))

    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.YEAR.value,
            agg_value="2023",
            kpi_value="whatever",
        )
    )

    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.MONTH.value,
            agg_value="2023-01",
            kpi_value="whatever",
        )
    )
    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.WEEK.value,
            agg_value="2023 W01",
            kpi_value="whatever",
        )
    )
    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id,
            agg_kind=AggKind.DAY.value,
            agg_value="2023-01-03",
            kpi_value="whatever",
        )
    )

    dbsession.add(PeriodDb.from_datetime(previous_datetime))

    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 4
    assert sorted(
        list(dbsession.execute(select(KpiValue.kpi_value)).scalars())
    ) == sorted(
        [
            previous_datetime_day_dummyvalue,
            previous_datetime_week_dummyvalue,
            previous_datetime_month_dummyvalue,
            previous_datetime_year_dummyvalue,
        ]
    )
