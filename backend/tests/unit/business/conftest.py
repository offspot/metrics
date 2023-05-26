from dataclasses import dataclass
from typing import Tuple

import pytest

from backend.business.indicators.indicator import IndicatorInterface
from backend.business.indicators.recorder import IntCounterRecorder, RecorderInterface
from backend.business.inputs.input import InputInterface


@dataclass
class TestInput(InputInterface):
    """Test input, with a content and a subfolder"""

    content: str
    subfolder: str


@dataclass
class AnotherTestInput(InputInterface):
    """Another test input, with nothing, just not supported by test indicators"""

    pass


class TotalIndicator(IndicatorInterface):
    """An indicator counting number of inputs, without any grouping"""

    def can_process_input(self, input: InputInterface) -> bool:
        if type(input) is TestInput:
            return True
        return False

    def create_new_recorder(self) -> RecorderInterface:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: InputInterface) -> Tuple[str]:
        return ()


class TotalByContentIndicator(IndicatorInterface):
    """An indicator counting number of test inputs, grouped by content"""

    def can_process_input(self, input: InputInterface) -> bool:
        if type(input) is TestInput:
            return True
        return False

    def create_new_recorder(self) -> RecorderInterface:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: TestInput) -> Tuple[str]:
        return (input.content,)


class TotalByContentAndSubfolderIndicator(IndicatorInterface):
    """An indicator counting number of test inputs, grouped by content and subfolder"""

    def can_process_input(self, input: InputInterface) -> bool:
        if type(input) is TestInput:
            return True
        return False

    def create_new_recorder(self) -> RecorderInterface:
        return IntCounterRecorder()

    def get_dimensions_values(self, input: TestInput) -> Tuple[str]:
        return (input.content, input.subfolder)


@pytest.fixture(scope="session")
def input1():
    yield TestInput(content="content1", subfolder="subfolder1")


@pytest.fixture(scope="session")
def input2():
    yield TestInput(content="content1", subfolder="subfolder2")


@pytest.fixture(scope="session")
def input3():
    yield TestInput(content="content2", subfolder="subfolder1")


@pytest.fixture(scope="session")
def another_input():
    yield AnotherTestInput()


@pytest.fixture()
def total_indicator() -> TotalIndicator:
    yield TotalIndicator()


@pytest.fixture()
def total_by_content_indicator() -> TotalByContentIndicator:
    yield TotalByContentIndicator()


@pytest.fixture()
def total_by_content_and_subfolder_indicator() -> TotalByContentIndicator:
    yield TotalByContentAndSubfolderIndicator()
