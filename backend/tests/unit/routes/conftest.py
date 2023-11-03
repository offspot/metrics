import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.orm import Session
from tests.unit.conftest import DummyKpi, DummyKpiValue

from offspot_metrics_backend.business.kpis.content_popularity import (
    ContentObjectPopularity,
    ContentObjectPopularityItem,
    ContentObjectPopularityValue,
    ContentPopularity,
    ContentPopularityItem,
    ContentPopularityValue,
)
from offspot_metrics_backend.business.kpis.shared_files import (
    SharedFiles,
    SharedFilesValue,
)
from offspot_metrics_backend.business.kpis.uptime import (
    Uptime,
    UptimeValue,
)
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.main import Main


@pytest.fixture(scope="session")
def event_loop():
    try:
        yield asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        yield loop
        loop.close()


@pytest.fixture()
def app(reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]):
    reverse_proxy_config("conf_no_packages.yaml")
    return Main().create_app()


@pytest_asyncio.fixture()  # pyright: ignore
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture()  # pyright: ignore
async def kpis(dbsession: Session) -> AsyncGenerator[list[KpiRecord], Any]:
    dbsession.execute(delete(KpiRecord))
    kpis = [
        KpiRecord(
            kpi_id=ContentObjectPopularity.unique_id,
            agg_kind="D",
            agg_value="2023-03-01",
            kpi_value=ContentObjectPopularityValue.model_validate(
                [
                    ContentObjectPopularityItem(
                        content="onecontent", item="oneitem", count=12, percentage=23.2
                    )
                ]
            ),
        ),
        KpiRecord(
            kpi_id=ContentPopularity.unique_id,
            agg_kind="D",
            agg_value="2023-03-01",
            kpi_value=ContentPopularityValue.model_validate(
                [ContentPopularityItem(content="onecontent", count=34, percentage=33.2)]
            ),
        ),
        KpiRecord(
            kpi_id=DummyKpi.unique_id,
            agg_kind="W",
            agg_value="2023 W10",
            kpi_value=DummyKpiValue.model_validate("199"),
        ),
        KpiRecord(
            kpi_id=SharedFiles.unique_id,
            agg_kind="W",
            agg_value="2023 W10",
            kpi_value=SharedFilesValue(files_created=65, files_deleted=45),
        ),
        KpiRecord(
            kpi_id=Uptime.unique_id,
            agg_kind="W",
            agg_value="2023 W10",
            kpi_value=UptimeValue(nb_minutes_on=654),
        ),
    ]
    for kpi in kpis:
        dbsession.add(kpi)
    dbsession.commit()
    yield kpis
    for kpi in kpis:
        dbsession.delete(kpi)
