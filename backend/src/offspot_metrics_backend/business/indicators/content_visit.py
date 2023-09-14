from typing import cast

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit as ContentHomeVisitInput,
)
from offspot_metrics_backend.business.inputs.content_visit import (
    ContentItemVisit as ContentItemVisitInput,
)
from offspot_metrics_backend.business.inputs.input import Input


class ContentHomeVisit(Indicator):
    """An indicator counting number of visit of a given content home page"""

    unique_id = 1001

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, ContentHomeVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(ContentHomeVisitInput, input_)
        return DimensionsValues(input_.content, None, None)


class ContentItemVisit(Indicator):
    """An indicator counting number of visit of a given content object"""

    unique_id = 1002

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, ContentItemVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(ContentItemVisitInput, input_)
        return DimensionsValues(input_.content, input_.item, None)
