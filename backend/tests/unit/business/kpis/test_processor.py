from datetime import datetime, timedelta
from typing import List

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.business.kpis.kpi import Kpi
from backend.business.kpis.processor import Processor
from backend.business.period import Period as PeriodBiz
from backend.db import count_from_stmt
from backend.db.models import IndicatorPeriod as PeriodDb
from backend.db.models import KpiValue


@pytest.mark.parametrize(
    "kind, now, expected_start_ts, expected_end_ts",
    [
        ("D", "2023-06-08 10:58:31", 1686182400, 1686268800),
        ("W", "2023-01-01 01:18:31", 1672012800, 1672617600),
        ("M", "2023-01-01 01:18:31", 1672531200, 1675209600),
        ("Y", "2023-01-01 01:18:31", 1672531200, 1704067200),
    ],
)
def test_timestamps(
    kind: str,
    now: str,
    expected_start_ts: int,
    expected_end_ts: int,
) -> None:
    res = Processor.get_timestamps(
        kind=kind, now=PeriodBiz(datetime.fromisoformat(now))
    )
    assert res.start == expected_start_ts
    assert res.stop == expected_end_ts


def test_timestamps_wrong_kind() -> None:
    with pytest.raises(AttributeError):
        Processor.get_timestamps(kind="Q", now=PeriodBiz(datetime.now()))


@pytest.mark.parametrize(
    "kind, now, expected_periods",
    [
        (
            "D",
            "2023-01-03 10:58:31",
            [f"2022-12-{i:02}" for i in range(28, 32)]
            + [f"2023-01-{i:02}" for i in range(1, 4)],
        ),
        (
            "W",
            "2023-01-03 01:18:31",
            [f"2022 W{i:02}" for i in range(50, 53)] + ["2023 W01"],
        ),
        (
            "M",
            "2023-01-03 01:18:31",
            [f"2022-{i:02}" for i in range(2, 13)] + ["2023-01"],
        ),
        ("Y", "2023-01-01 01:18:31", None),
    ],
)
def test_get_periods_to_keep(
    kind: str,
    now: str,
    expected_periods: List[str] | None,
) -> None:
    res = Processor.get_periods_to_keep(
        kind=kind, now=PeriodBiz(datetime.fromisoformat(now))
    )
    if not expected_periods:
        assert res is None
    else:
        assert res is not None
        assert sorted(res) == sorted(expected_periods)


def test_get_periods_to_keep_wrong_kind() -> None:
    with pytest.raises(AttributeError):
        Processor.get_periods_to_keep(kind="Q", now=PeriodBiz(datetime.now()))


def test_process_tick(
    processor: Processor, dummy_kpi: Kpi, init_datetime: datetime, dbsession: Session
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiValue))
    processor.process_tick(now=PeriodBiz(init_datetime), session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 0
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(minutes=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 0
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(hours=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 3
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(hours=4)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 3
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=1)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 4
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=1) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 5
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "D - 1686268800 - 1686355200",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=2)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 5
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "D - 1686268800 - 1686355200",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=2) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 6
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "D - 1686268800 - 1686355200",
            "D - 1686355200 - 1686441600",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=7)), session=dbsession
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 6
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686182400 - 1686268800",
            "D - 1686268800 - 1686355200",
            "D - 1686355200 - 1686441600",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )
    processor.process_tick(
        now=PeriodBiz(init_datetime + timedelta(days=7) + timedelta(hours=1)),
        session=dbsession,
    )
    assert count_from_stmt(dbsession, select(KpiValue)) == 7
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686268800 - 1686355200",
            "D - 1686355200 - 1686441600",
            "D - 1686787200 - 1686873600",
            "W - 1685923200 - 1686528000",
            "W - 1686528000 - 1687132800",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
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
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1686096000 - 1686182400",
            "W - 1685923200 - 1686528000",
            "M - 1685577600 - 1688169600",
            "Y - 1672531200 - 1704067200",
        ]
    )


def test_restore_kpis_from_filled_db(
    processor: Processor, dummy_kpi: Kpi, init_datetime: datetime, dbsession: Session
) -> None:
    processor.kpis = [dummy_kpi]
    dbsession.execute(delete(KpiValue))
    dbsession.execute(delete(PeriodDb))

    dbsession.add(
        KpiValue(kpi_id=dummy_kpi.unique_id, kind="Y", period="2023", value="whatever")
    )

    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id, kind="M", period="2023-01", value="whatever"
        )
    )
    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id, kind="W", period="2023 W01", value="whatever"
        )
    )
    dbsession.add(
        KpiValue(
            kpi_id=dummy_kpi.unique_id, kind="D", period="2023-01-03", value="whatever"
        )
    )

    dbsession.add(PeriodDb.from_datetime(datetime.fromisoformat("2023-01-03 10:58:00")))

    processor.restore_from_db(session=dbsession)
    assert count_from_stmt(dbsession, select(KpiValue)) == 4
    assert sorted(list(dbsession.execute(select(KpiValue.value)).scalars())) == sorted(
        [
            "D - 1672704000 - 1672790400",
            "W - 1672617600 - 1673222400",
            "M - 1672531200 - 1675209600",
            "Y - 1672531200 - 1704067200",
        ]
    )