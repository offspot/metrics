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
        {"kind": "W", "value": "2023 W11"},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "agg_kind, expected_result",
    [
        [
            "D",
            {
                "aggKind": "D",
                "valuesAvailable": ["2023-02-28", "2023-03-01"],
                "kpis": [
                    {
                        "kpiId": 2001,
                        "values": [
                            {
                                "aggValue": "2023-03-01",
                                "kpiValue": {
                                    "items": [{"package": "onecontent", "visits": 34}],
                                    "totalVisits": 45,
                                },
                            }
                        ],
                    },
                    {
                        "kpiId": 2004,
                        "values": [
                            {"aggValue": "2023-02-28", "kpiValue": {"nbMinutesOn": 456}}
                        ],
                    },
                ],
            },
        ],
        [
            "W",
            {
                "aggKind": "W",
                "valuesAvailable": ["2023 W10", "2023 W11"],
                "kpis": [
                    {
                        "kpiId": -2001,
                        "values": [
                            {"aggValue": "2023 W10", "kpiValue": {"root": "199"}}
                        ],
                    },
                    {
                        "kpiId": 2003,
                        "values": [
                            {
                                "aggValue": "2023 W10",
                                "kpiValue": {
                                    "items": [
                                        {
                                            "minutesActivity": 98,
                                            "package": "othercontent",
                                        }
                                    ],
                                    "totalMinutesActivity": 143,
                                },
                            }
                        ],
                    },
                    {
                        "kpiId": 2004,
                        "values": [
                            {"aggValue": "2023 W10", "kpiValue": {"nbMinutesOn": 654}},
                            {"aggValue": "2023 W11", "kpiValue": {"nbMinutesOn": 235}},
                        ],
                    },
                    {
                        "kpiId": 2005,
                        "values": [
                            {
                                "aggValue": "2023 W10",
                                "kpiValue": {"filesCreated": 65, "filesDeleted": 45},
                            }
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
