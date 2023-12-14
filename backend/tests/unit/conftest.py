import pathlib
from collections.abc import Callable, Generator

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.constants import BackendConf
from offspot_metrics_backend.db.models import KpiValue


@pytest.fixture()
def reverse_proxy_config() -> (
    Generator[Callable[[str | None], ReverseProxyConfig], None, None]
):
    previous_location = BackendConf.package_conf_file_location

    def _reverse_proxy_config(location: str | None) -> ReverseProxyConfig:
        if location:
            path = (
                pathlib.Path(__file__)
                .parent.absolute()
                .joinpath("conf_files", location)
            )
            BackendConf.package_conf_file_location = str(path)
        config = ReverseProxyConfig()
        config.parse_configuration()
        return config

    yield _reverse_proxy_config

    BackendConf.package_conf_file_location = previous_location


class DummyKpiValue(KpiValue):
    root: str

    def __lt__(self, other: "DummyKpiValue") -> bool:
        """Custom comparator just to make tests more easy"""
        return self.root < other.root


class DummyKpi(Kpi):
    """A dummy KPI which is not using indicators at all to simplify testing"""

    unique_id = -2001  # this ID is unique to each kind of kpi

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,
        start_ts: int,
        stop_ts: int,
        session: Session,  # noqa: ARG002
    ) -> DummyKpiValue:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""
        return DummyKpiValue(root=f"{agg_kind.value} - {start_ts} - {stop_ts}")
