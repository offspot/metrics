from typing import cast

from ..inputs.content_visit import ContentHomeVisit as ContentHomeVisitInput
from ..inputs.content_visit import ContentObjectVisit as ContentObjectVisitInput
from ..inputs.input import Input
from .dimensions import DimensionsValues
from .indicator import Indicator
from .recorder import IntCounterRecorder, Recorder


class ContentHomeVisit(Indicator):
    """An indicator counting number of visit of a given content home page"""

    unique_id = 1001

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, ContentHomeVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input_ = cast(ContentHomeVisitInput, input)
        return DimensionsValues(input_.content, None, None)


class ContentObjectVisit(Indicator):
    """An indicator counting number of visit of a given content object"""

    unique_id = 1002

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, ContentObjectVisitInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input_ = cast(ContentObjectVisitInput, input)
        return DimensionsValues(input_.content, input_.item, None)
