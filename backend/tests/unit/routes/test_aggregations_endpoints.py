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
                "aggKind": "D",
                "aggregations": [
                    {
                        "aggValue": "2023-02-28",
                        "kpis": [{"kpiId": 2004, "value": {"nbMinutesOn": 456}}],
                    },
                    {
                        "aggValue": "2023-03-01",
                        "kpis": [
                            {
                                "kpiId": 2001,
                                "value": {
                                    "items": [{"package": "onecontent", "visits": 34}],
                                    "totalVisits": 45,
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
                "aggKind": "W",
                "aggregations": [
                    {
                        "aggValue": "2023 W10",
                        "kpis": [
                            {
                                "kpiId": -2001,
                                "value": "199",
                            },
                            {
                                "kpiId": 2003,
                                "value": {
                                    "items": [
                                        {
                                            "minutesActivity": 98,
                                            "package": "othercontent",
                                        }
                                    ],
                                    "totalMinutesActivity": 143,
                                },
                            },
                            {"kpiId": 2004, "value": {"nbMinutesOn": 654}},
                            {
                                "kpiId": 2005,
                                "value": {"filesCreated": 65, "filesDeleted": 45},
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
