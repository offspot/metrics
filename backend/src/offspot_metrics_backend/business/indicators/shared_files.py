from typing import cast

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.inputs.shared_files import SharedFilesOperation


class SharedFilesOperations(Indicator):
    """An indicator counting operations on shared files"""

    unique_id = 1003

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, SharedFilesOperation)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(SharedFilesOperation, input_)
        return DimensionsValues(input_.kind, None, None)
