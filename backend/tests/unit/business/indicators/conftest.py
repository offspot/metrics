from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias, cast

import pytest

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.indicators.processor import Processor
from offspot_metrics_backend.business.indicators.recorder import (
    IntCounterRecorder,
    Recorder,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.period import Period

IndicatorGenerator: TypeAlias = Generator[Indicator, None, None]
InputGenerator: TypeAlias = Generator[Input, None, None]
ProcessorGenerator: TypeAlias = Generator[Processor, None, None]


class FailingRecorder(Recorder):
    """A recorder that fails to process input"""

    def process_input(
        self,
        input_: Input,  # noqa: ARG002
    ) -> None:
        """Processing an input consists simply in raising an exception"""
        raise ValueError()

    @property
    def value(self) -> int:
        """Retrieving the value consists simply is raising an exception"""
        raise ValueError()

    @property
    def state(self) -> str:
        """Fails to retrieve state"""
        raise ValueError()

    def restore_state(self, value: str):  # noqa: ARG002
        """Fails to restore state"""
        raise ValueError()


@dataclass
class TestInput(Input):
    """Test input, with a content and a subfolder"""

    content: str
    subfolder: str


@dataclass
class AnotherTestInput(Input):
    """Another test input, with nothing, just not supported by test indicators"""

    ...


class TotalIndicator(Indicator):
    """An indicator counting number of inputs, without any grouping"""

    unique_id = -1001

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, TestInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:  # noqa: ARG002
        return DimensionsValues(None, None, None)


class TotalByContentIndicator(Indicator):
    """An indicator counting number of test inputs, grouped by content"""

    unique_id = -1002

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, TestInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(TestInput, input_)
        return DimensionsValues(input_.content, None, None)


class FailingIndicator(Indicator):
    """An indicator that fails to process input"""

    unique_id = -1004

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, TestInput)

    def get_new_recorder(self) -> Recorder:
        return FailingRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:  # noqa: ARG002
        return DimensionsValues(None, None, None)


class TotalByContentAndSubfolderIndicator(Indicator):
    """An indicator counting number of test inputs, grouped by content and subfolder"""

    unique_id = -1003

    def can_process_input(self, input_: Input) -> bool:
        return isinstance(input_, TestInput)

    def get_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input_: Input) -> DimensionsValues:
        input_ = cast(TestInput, input_)
        return DimensionsValues(input_.content, input_.subfolder, None)


@pytest.fixture(scope="session")
def input1() -> InputGenerator:
    yield TestInput(content="content1", subfolder="subfolder1")


@pytest.fixture(scope="session")
def input2() -> InputGenerator:
    yield TestInput(content="content1", subfolder="subfolder2")


@pytest.fixture(scope="session")
def input3() -> InputGenerator:
    yield TestInput(content="content2", subfolder="subfolder1")


@pytest.fixture(scope="session")
def another_input() -> InputGenerator:
    yield AnotherTestInput()


@pytest.fixture()
def total_indicator() -> IndicatorGenerator:
    yield TotalIndicator()


@pytest.fixture()
def total_by_content_indicator() -> IndicatorGenerator:
    yield TotalByContentIndicator()


@pytest.fixture()
def total_by_content_and_subfolder_indicator() -> IndicatorGenerator:
    yield TotalByContentAndSubfolderIndicator()


@pytest.fixture()
def processor(init_datetime: datetime) -> ProcessorGenerator:
    yield Processor(Period(init_datetime))


@pytest.fixture()
def failing_indicator() -> IndicatorGenerator:
    yield FailingIndicator()
