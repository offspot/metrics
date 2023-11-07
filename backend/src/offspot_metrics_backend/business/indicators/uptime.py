from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.clock_tick import ClockTick
from offspot_metrics_backend.business.inputs.input import Input


class Uptime(Indicator):
    """An indicator counting the offspot uptime"""

    unique_id = 1004

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, ClockTick)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:  # noqa: ARG002
        return DimensionsValues(None, None, None)
