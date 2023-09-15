import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.db.models import KpiRecord, DummyKpiValue
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
            kpi_id=1,
            agg_kind="D",
            agg_value="2023-03-01",
            kpi_value=DummyKpiValue("165"),
        ),
        KpiRecord(
            kpi_id=2,
            agg_kind="D",
            agg_value="2023-03-01",
            kpi_value=DummyKpiValue("123"),
        ),
        KpiRecord(
            kpi_id=1, agg_kind="W", agg_value="2023 W10", kpi_value=DummyKpiValue("199")
        ),
    ]
    for kpi in kpis:
        dbsession.add(kpi)
    dbsession.commit()
    yield kpis
    for kpi in kpis:
        dbsession.delete(kpi)
