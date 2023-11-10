from typing import cast

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    Recorder,
    UsageRecorder,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.inputs.package import PackageRequest


class TotalUsageOverall(Indicator):
    """An indicator counting usage activity on all packages"""

    unique_id = 1005

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, PackageRequest)

    def get_new_recorder(self) -> Recorder:
        return UsageRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:  # noqa: ARG002
        return DimensionsValues(None, None, None)


class TotalUsageByPackage(Indicator):
    """An indicator counting usage activity by packages"""

    unique_id = 1006

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, PackageRequest)

    def get_new_recorder(self) -> Recorder:
        return UsageRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(PackageRequest, input_)
        return DimensionsValues(input_.package_title, None, None)
