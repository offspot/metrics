from typing import Tuple

import pytest

from backend.business.indicators.indicator import IndicatorInterface
from backend.business.indicators.recorder import IntCounterRecorder, RecorderInterface
from backend.business.inputs.input import InputInterface


class SampleGenericIndicator(IndicatorInterface):
    def create_new_recorder(self) -> RecorderInterface:
        return IntCounterRecorder()

    def can_process_input(self, input: InputInterface) -> bool:
        return True

    def get_dimensions_values(self, input: InputInterface) -> Tuple[str]:
        return ()


@pytest.mark.parametrize(
    "subclass, parentclass",
    [
        (SampleGenericIndicator, IndicatorInterface),
        (IntCounterRecorder, RecorderInterface),
    ],
)
def test_subclass(subclass, parentclass):
    assert issubclass(subclass, parentclass)


@pytest.mark.parametrize(
    "abstractclass",
    [
        IndicatorInterface,
        RecorderInterface,
    ],
)
def test_abstract_class(abstractclass):
    with pytest.raises(TypeError):
        abstractclass()


@pytest.mark.parametrize(
    "concreteclass",
    [
        SampleGenericIndicator,
        IntCounterRecorder,
    ],
)
def test_concrete_class(concreteclass):
    concreteclass()
