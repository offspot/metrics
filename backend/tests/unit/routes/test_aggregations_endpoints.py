from typing import List

from httpx import AsyncClient

from backend.db.models import KpiValue
from backend.main import PREFIX


async def test_aggregations(client: AsyncClient, kpis: List[KpiValue]):
    response = await client.get(f"{PREFIX}/aggregations")
    assert response.status_code == 200
    response_json = response.json()
    assert "aggregations" in response_json
    assert len(response_json["aggregations"]) == 2
    assert "kind" in response_json["aggregations"][0]
    assert "value" in response_json["aggregations"][0]
