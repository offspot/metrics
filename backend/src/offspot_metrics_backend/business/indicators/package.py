from typing import cast

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.inputs.package import (
    PackageHomeVisit as PackageHomeVisitInput,
)
from offspot_metrics_backend.business.inputs.package import (
    PackageItemVisit as PackageItemVisitInput,
)


class PackageHomeVisit(Indicator):
    """An indicator counting number of visit of a given package home page"""

    unique_id = 1001

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, PackageHomeVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(PackageHomeVisitInput, input_)
        return DimensionsValues(input_.package_title, None, None)


class PackageItemVisit(Indicator):
    """An indicator counting number of visit of a given package item"""

    unique_id = 1002

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, PackageItemVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(PackageItemVisitInput, input_)
        return DimensionsValues(input_.package_title, input_.item_path, None)
