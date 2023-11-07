from http import HTTPStatus

import pytest
from httpx import AsyncClient

from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.main import PREFIX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kpi_id, agg_kind, agg_value, expected_value",
    [
        (
            2001,
            "D",
            "2023-03-01",
            [{"content": "onecontent", "count": 34, "percentage": 33.2}],
        ),
        (
            2002,
            "D",
            "2023-03-01",
            [
                {
                    "content": "onecontent",
                    "count": 12,
                    "item": "oneitem",
                    "percentage": 23.2,
                }
            ],
        ),
        (
            2004,
            "W",
            "2023 W10",
            {"nb_minutes_on": 654},
        ),
        (
            2005,
            "W",
            "2023 W10",
            {"files_created": 65, "files_deleted": 45},
        ),
        (-2001, "W", "2023 W10", "199"),
    ],
)
async def test_kpis_get(
    kpi_id: int,
    agg_kind: str,
    agg_value: str,
    expected_value: str,
    client: AsyncClient,
    kpis: list[KpiRecord],  # noqa: ARG001
):
    response = await client.get(
        f"{PREFIX}/kpis/{kpi_id}/values?agg_kind={agg_kind}&agg_value={agg_value}"
    )
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert "kpi_id" in response_json
    assert "value" in response_json
    assert response_json["kpi_id"] == kpi_id
    assert response_json["value"] == expected_value


@pytest.mark.asyncio
async def test_kpis_not_exist(
    client: AsyncClient,
    kpis: list[KpiRecord],  # noqa: ARG001
):
    response = await client.get(
        f"{PREFIX}/kpis/whatever/values?agg_kind=W&agg_value=whatever"
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_kpis_wrong_agg_kind(
    client: AsyncClient,
    kpis: list[KpiRecord],  # noqa: ARG001
):
    response = await client.get(
        f"{PREFIX}/kpis/whatever/values?agg_kind=whatever&agg_value=whatever"
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
