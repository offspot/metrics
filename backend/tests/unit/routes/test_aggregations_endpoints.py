from http import HTTPStatus

import pytest
from httpx import AsyncClient

from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.main import PREFIX


@pytest.mark.asyncio
async def test_aggregations(
    client: AsyncClient,
    kpis: list[KpiRecord],  # noqa: ARG001
):
    response = await client.get(f"{PREFIX}/aggregations")
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert "aggregations" in response_json
    assert len(response_json["aggregations"]) == 2
    assert "kind" in response_json["aggregations"][0]
    assert "value" in response_json["aggregations"][0]
