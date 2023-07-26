import pytest

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.input import Input


class SampleGenericIndicator(Indicator):
    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def can_process_input(self, input_: Input) -> bool:  # noqa: ARG002
        return True

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:  # noqa: ARG002
        return DimensionsValues(None, None, None)


@pytest.mark.parametrize(
    "subclass, parentclass",
    [
        (SampleGenericIndicator, Indicator),
        (IntCounterRecorder, Recorder),
    ],
)
def test_subclass(subclass: type, parentclass: type) -> None:
    assert issubclass(subclass, parentclass)


@pytest.mark.parametrize(
    "abstractclass",
    [
        Indicator,
        Recorder,
    ],
)
def test_abstract_class(abstractclass: type) -> None:
    with pytest.raises(TypeError):
        abstractclass()


@pytest.mark.parametrize(
    "concreteclass",
    [
        SampleGenericIndicator,
        IntCounterRecorder,
    ],
)
def test_concrete_class(concreteclass: type) -> None:
    concreteclass()
