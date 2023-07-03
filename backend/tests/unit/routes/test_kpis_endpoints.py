from typing import List

import pytest
from httpx import AsyncClient

from backend.db.models import KpiValue
from backend.main import PREFIX


@pytest.mark.parametrize(
    "kpi_id, agg_kind, agg_value, expected_value",
    [
        (1, "D", "2023-03-01", "165"),
        (1, "W", "2023 W10", "199"),
        (2, "D", "2023-03-01", "123"),
    ],
)
async def test_kpis(
    kpi_id: int,
    agg_kind: str,
    agg_value: str,
    expected_value: str,
    client: AsyncClient,
    kpis: List[KpiValue],
):
    response = await client.get(
        f"{PREFIX}/kpis/{kpi_id}/values?agg_kind={agg_kind}&agg_value={agg_value}"
    )
    assert response.status_code == 200
    response_json = response.json()
    assert "id" in response_json
    assert "value" in response_json
    assert response_json["id"] == kpi_id
    assert response_json["value"] == expected_value


async def test_kpis_not_exist(
    client: AsyncClient,
    kpis: List[KpiValue],
):
    response = await client.get(
        f"{PREFIX}/kpis/whatever/values?agg_kind=whatever&agg_value=whatever"
    )
    assert response.status_code == 404
