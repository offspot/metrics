from dataclasses import dataclass
from datetime import datetime
from typing import Generator, TypeAlias, cast

import pytest

from backend.business.indicators import DimensionsValues
from backend.business.indicators.indicator import Indicator
from backend.business.indicators.processor import Processor
from backend.business.indicators.recorder import IntCounterRecorder, Recorder
from backend.business.inputs.input import Input

IndicatorGenerator: TypeAlias = Generator[Indicator, None, None]
InputGenerator: TypeAlias = Generator[Input, None, None]
ProcessorGenerator: TypeAlias = Generator[Processor, None, None]


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

    unique_id = -1

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, TestInput)

    def create_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        return tuple()


class TotalByContentIndicator(Indicator):
    """An indicator counting number of test inputs, grouped by content"""

    unique_id = -2

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, TestInput)

    def create_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input = cast(TestInput, input)
        return (input.content,)


class TotalByContentAndSubfolderIndicator(Indicator):
    """An indicator counting number of test inputs, grouped by content and subfolder"""

    unique_id = -3

    def can_process_input(self, input: Input) -> bool:
        return isinstance(input, TestInput)

    def create_new_recorder(self) -> Recorder:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: Input) -> DimensionsValues:
        input = cast(TestInput, input)
        return (input.content, input.subfolder)


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
    yield Processor(init_datetime)
