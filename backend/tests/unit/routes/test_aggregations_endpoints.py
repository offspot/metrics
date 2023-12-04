from http import HTTPStatus
from typing import Any

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
    assert response_json["aggregations"] == [
        {"kind": "D", "value": "2023-02-28"},
        {"kind": "D", "value": "2023-03-01"},
        {"kind": "W", "value": "2023 W10"},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "agg_kind, expected_result",
    [
        [
            "D",
            {
                "agg_kind": "D",
                "aggregations": [
                    {
                        "agg_value": "2023-02-28",
                        "kpis": [{"kpi_id": 2004, "value": {"nb_minutes_on": 456}}],
                    },
                    {
                        "agg_value": "2023-03-01",
                        "kpis": [
                            {
                                "kpi_id": 2001,
                                "value": {
                                    "items": [{"package": "onecontent", "visits": 34}],
                                    "total_visits": 45,
                                },
                            },
                        ],
                    },
                ],
            },
        ],
        [
            "W",
            {
                "agg_kind": "W",
                "aggregations": [
                    {
                        "agg_value": "2023 W10",
                        "kpis": [
                            {
                                "kpi_id": -2001,
                                "value": "199",
                            },
                            {
                                "kpi_id": 2003,
                                "value": {
                                    "items": [
                                        {
                                            "minutes_activity": 98,
                                            "package": "othercontent",
                                        }
                                    ],
                                    "total_minutes_activity": 143,
                                },
                            },
                            {"kpi_id": 2004, "value": {"nb_minutes_on": 654}},
                            {
                                "kpi_id": 2005,
                                "value": {"files_created": 65, "files_deleted": 45},
                            },
                        ],
                    },
                ],
            },
        ],
    ],
)
async def test_aggregation_by_kind(
    agg_kind: str,
    expected_result: dict[str, Any],
    client: AsyncClient,
    kpis: list[KpiRecord],  # noqa: ARG001
):
    response = await client.get(f"{PREFIX}/aggregations/{agg_kind}")
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json == expected_result
