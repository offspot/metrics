from typing import cast

from ..inputs.content_visit import ContentHomeVisit as ContentHomeVisitInput
from ..inputs.content_visit import ContentObjectVisit as ContentObjectVisitInput
from ..inputs.input import Input
from . import DimensionsValues
from .indicator import Indicator
from .recorder import IntCounterRecorder, Recorder

CONTENT_HOME_VISIT_ID = 1
CONTENT_OBJECT_VISIT_ID = 2


class ContentHomeVisit(Indicator):
    """An indicator counting number of visit of a given content home page"""

    unique_id = CONTENT_HOME_VISIT_ID

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, ContentHomeVisitInput)

    def create_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input = cast(ContentHomeVisitInput, input)
        return (input.content,)


class ContentObjectVisit(Indicator):
    """An indicator counting number of visit of a given content object"""

    unique_id = CONTENT_OBJECT_VISIT_ID

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, ContentObjectVisitInput)

    def create_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input = cast(ContentObjectVisitInput, input)
        return (
            input.content,
            input.object,
        )
