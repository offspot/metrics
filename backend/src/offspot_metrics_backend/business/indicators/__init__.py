from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.package import (
    PackageHomeVisit,
    PackageItemVisit,
)
from offspot_metrics_backend.business.indicators.shared_files import (
    SharedFilesOperations,
)
from offspot_metrics_backend.business.indicators.total_usage import (
    TotalUsageByPackage,
    TotalUsageOverall,
)
from offspot_metrics_backend.business.indicators.uptime import Uptime

__all__ = [
    "PackageHomeVisit",
    "PackageItemVisit",
    "SharedFilesOperations",
    "TotalUsageOverall",
    "TotalUsageByPackage",
    "Uptime",
]
ALL_INDICATORS: list[Indicator] = [globals()[klass]() for klass in __all__]


def get_indicator_name(indicator_id: int) -> str:
    for indicator in ALL_INDICATORS:
        if indicator.unique_id == indicator_id:
            return type(indicator).__name__
    raise ValueError(f"Unknown indicator id {indicator_id}")
