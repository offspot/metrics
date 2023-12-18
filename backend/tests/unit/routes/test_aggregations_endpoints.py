from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.db.models import KpiRecord
from offspot_metrics_backend.main import PREFIX
from offspot_metrics_backend.routes.aggregations import get_all_values


@pytest.mark.parametrize(
    "kind,values_available,expected_all_values",
    [
        (AggKind.MONTH, [], []),
        (AggKind.YEAR, ["2023"], ["2023"]),
        (AggKind.YEAR, ["2023", "2024"], ["2023", "2024"]),
        (AggKind.YEAR, ["2023", "2026"], ["2023", "2024", "2025", "2026"]),
        (AggKind.MONTH, ["2023-02"], ["2022-12", "2023-01", "2023-02"]),
        (AggKind.WEEK, ["2023 W02"], ["2022 W51", "2022 W52", "2023 W01", "2023 W02"]),
        (
            AggKind.DAY,
            ["2024-03-01"],
            [
                "2024-02-24",
                "2024-02-25",
                "2024-02-26",
                "2024-02-27",
                "2024-02-28",
                "2024-02-29",
                "2024-03-01",
            ],
        ),
    ],
)
def test_aggregations_all_values(
    kind: AggKind, values_available: list[str], expected_all_values: list[str]
):
    assert (
        get_all_values(agg_kind=kind, values_available=values_available)
        == expected_all_values
    )


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
                "valuesAll": [
                    "2023-02-23",
                    "2023-02-24",
                    "2023-02-25",
                    "2023-02-26",
                    "2023-02-27",
                    "2023-02-28",
                    "2023-03-01",
                ],
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
                "valuesAll": ["2023 W08", "2023 W09", "2023 W10", "2023 W11"],
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
