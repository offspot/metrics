from backend.business.indicators.indicator import IndicatorInterface
from backend.business.indicators.processor import Processor
from backend.business.indicators.record import Record
from backend.business.inputs.input import InputInterface


def test_no_input(total_indicator: IndicatorInterface):
    processor = Processor()
    processor.indicators.append(total_indicator)
    records = list(total_indicator.get_records())
    assert len(records) == 0


def test_one_input(input1: InputInterface, total_indicator: IndicatorInterface):
    processor = Processor()
    processor.indicators = [total_indicator]
    processor.process_input(input1)
    records = list(total_indicator.get_records())
    expected_records = [
        Record(value=1, dimensions=()),
    ]
    assert records == expected_records


def test_one_input_repeated(
    input1: InputInterface, total_indicator: IndicatorInterface
):
    processor = Processor()
    processor.indicators = [total_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    records = list(total_indicator.get_records())
    expected_records = [
        Record(value=2, dimensions=()),
    ]
    assert records == expected_records


def test_another_input(
    total_indicator: IndicatorInterface, another_input: InputInterface
):
    processor = Processor()
    processor.indicators = [total_indicator]
    processor.process_input(another_input)
    records = list(total_indicator.get_records())
    assert len(records) == 0


def test_total_by_content(
    input1: InputInterface,
    input2: InputInterface,
    input3: InputInterface,
    another_input: InputInterface,
    total_by_content_indicator: IndicatorInterface,
):
    processor = Processor()
    processor.indicators = [total_by_content_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    records = list(total_by_content_indicator.get_records())
    expected_records = [
        Record(value=3, dimensions=("content1",)),
        Record(value=1, dimensions=("content2",)),
    ]
    assert records == expected_records


def test_total_by_content_and_subfolder(
    input1: InputInterface,
    input2: InputInterface,
    input3: InputInterface,
    another_input: InputInterface,
    total_by_content_and_subfolder_indicator: IndicatorInterface,
):
    processor = Processor()
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    records = list(total_by_content_and_subfolder_indicator.get_records())
    expected_records = [
        Record(value=2, dimensions=("content1", "subfolder1")),
        Record(value=1, dimensions=("content1", "subfolder2")),
        Record(value=1, dimensions=("content2", "subfolder1")),
    ]
    assert records == expected_records


def test_reset(
    input1: InputInterface,
    input2: InputInterface,
    input3: InputInterface,
    another_input: InputInterface,
    total_by_content_and_subfolder_indicator: IndicatorInterface,
):
    processor = Processor()
    processor.indicators = [total_by_content_and_subfolder_indicator]
    processor.process_input(input1)
    processor.process_input(input1)
    processor.process_input(input2)
    processor.process_input(another_input)
    processor.process_input(input3)
    processor.reset_state()
    processor.process_input(input1)
    processor.process_input(input2)
    records = list(total_by_content_and_subfolder_indicator.get_records())
    expected_records = [
        Record(value=1, dimensions=("content1", "subfolder1")),
        Record(value=1, dimensions=("content1", "subfolder2")),
    ]
    assert records == expected_records
