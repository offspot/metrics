from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.business.kpis.popularity import (
    PackagePopularity,
    PopularPages,
)
from offspot_metrics_backend.business.kpis.shared_files import SharedFiles
from offspot_metrics_backend.business.kpis.total_usage import TotalUsage
from offspot_metrics_backend.business.kpis.uptime import Uptime

__all__ = ["PackagePopularity", "PopularPages", "SharedFiles", "TotalUsage", "Uptime"]

ALL_KPIS: list[Kpi] = [globals()[klass]() for klass in __all__]


def get_kpi_name(kpi_id: int) -> str:
    for kpi in ALL_KPIS:
        if kpi.unique_id == kpi_id:
            return type(kpi).__name__
    raise ValueError(f"Unknown kpi id {kpi_id}")
