import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from offspot_metrics_backend.db.models import KpiValue
from offspot_metrics_backend.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    try:
        yield asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        yield loop
        loop.close()


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest_asyncio.fixture(scope="session")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture()
async def kpis(dbsession: Session) -> AsyncGenerator[list[KpiValue], Any]:
    dbsession.execute(delete(KpiValue))
    kpis = [
        KpiValue(kpi_id=1, agg_kind="D", agg_value="2023-03-01", kpi_value="165"),
        KpiValue(kpi_id=2, agg_kind="D", agg_value="2023-03-01", kpi_value="123"),
        KpiValue(kpi_id=1, agg_kind="W", agg_value="2023 W10", kpi_value="199"),
    ]
    for kpi in kpis:
        dbsession.add(kpi)
    dbsession.commit()
    yield kpis
    for kpi in kpis:
        dbsession.delete(kpi)
