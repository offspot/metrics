import datetime

import pytest

from offspot_metrics_backend.business.exceptions import (
    TooWideUsageError,
    WrongInputTypeError,
)
from offspot_metrics_backend.business.indicators.recorder import (
    UsageRecorder,
)
from offspot_metrics_backend.business.inputs.input import Input, TimedInput

START_TIME = datetime.datetime.fromisoformat("2022-09-08 11:00:00")


def get_timed_input(minutes: int = 0, seconds: int = 0) -> TimedInput:
    return TimedInput(
        ts=START_TIME + datetime.timedelta(minutes=minutes, seconds=seconds)
    )


class TestUsageRecorder:
    @pytest.mark.parametrize(
        "inputs, expected_value",
        [
            ([], 0),
            ([get_timed_input()], 10),
            ([get_timed_input(seconds=12)], 10),
            ([get_timed_input(minutes=1, seconds=12)], 10),
            (
                [
                    get_timed_input(),
                    get_timed_input(minutes=1, seconds=12),
                    get_timed_input(minutes=9, seconds=59),
                ],
                10,
            ),
            (
                [
                    get_timed_input(seconds=59),
                    get_timed_input(minutes=1, seconds=12),
                    get_timed_input(minutes=9, seconds=59),
                ],
                10,
            ),
            (
                [get_timed_input(minutes=1), get_timed_input(minutes=10)],
                10,
            ),
            (
                [
                    get_timed_input(seconds=59),
                    get_timed_input(minutes=10),
                ],
                20,
            ),
            (
                [
                    get_timed_input(seconds=59),
                    get_timed_input(minutes=40, seconds=00),
                ],
                20,
            ),
            (
                [
                    get_timed_input(seconds=2),
                    get_timed_input(minutes=40, seconds=00),
                ],
                20,
            ),
            (
                [
                    get_timed_input(seconds=-2),
                    get_timed_input(minutes=8, seconds=00),
                    get_timed_input(minutes=23, seconds=00),
                    get_timed_input(minutes=38, seconds=00),
                    get_timed_input(minutes=40, seconds=00),
                ],
                40,
            ),
            (
                [
                    get_timed_input(seconds=-2),
                    get_timed_input(minutes=8, seconds=00),
                    get_timed_input(minutes=23, seconds=00),
                    get_timed_input(minutes=39, seconds=00),
                    get_timed_input(minutes=40, seconds=00),
                ],
                30,
            ),
            (
                [
                    get_timed_input(seconds=-2),
                    get_timed_input(minutes=59, seconds=30),
                ],
                20,
            ),
            (
                [
                    get_timed_input(seconds=-2),
                    get_timed_input(minutes=10, seconds=00),
                    get_timed_input(minutes=21, seconds=00),
                    get_timed_input(minutes=32, seconds=00),
                    get_timed_input(minutes=43, seconds=00),
                    get_timed_input(minutes=49, seconds=00),
                    get_timed_input(minutes=52, seconds=00),
                ],
                60,
            ),
            (
                [
                    get_timed_input(seconds=-2),
                    get_timed_input(minutes=10, seconds=00),
                    get_timed_input(minutes=21, seconds=00),
                    get_timed_input(minutes=32, seconds=00),
                    get_timed_input(minutes=43, seconds=00),
                    get_timed_input(minutes=49, seconds=00),
                    get_timed_input(minutes=59, seconds=00),
                ],
                60,
            ),
            (
                [
                    get_timed_input(minutes=-14),
                    get_timed_input(minutes=-1),
                ],
                20,
            ),
            (
                [
                    get_timed_input(minutes=-14),
                    get_timed_input(minutes=-1),
                    get_timed_input(minutes=30),
                ],
                30,
            ),
            (
                [
                    get_timed_input(),
                    get_timed_input(minutes=60, seconds=1),
                ],
                20,
            ),
            (
                [
                    get_timed_input(),
                    get_timed_input(minutes=59),
                    get_timed_input(minutes=60, seconds=1),
                ],
                20,
            ),
            (
                [
                    get_timed_input(),
                    get_timed_input(minutes=21),
                    get_timed_input(minutes=59),
                    get_timed_input(minutes=61, seconds=1),
                ],
                30,
            ),
            (
                [
                    get_timed_input(),
                    get_timed_input(minutes=10),
                    get_timed_input(minutes=20),
                    get_timed_input(minutes=30),
                    get_timed_input(minutes=40),
                    get_timed_input(minutes=50),
                    get_timed_input(minutes=59),
                    get_timed_input(minutes=60),
                ],
                60,
            ),
        ],
    )
    def test_recorder_value(self, inputs: list[TimedInput], expected_value: int):
        recorder = UsageRecorder()
        for input_ in inputs:
            recorder.process_input(input_=input_)
        assert recorder.value == expected_value

    def test_recorder_state(self):
        recorder = UsageRecorder()
        for input_ in [
            get_timed_input(minutes=1),
            get_timed_input(minutes=1, seconds=12),
            get_timed_input(minutes=52),
        ]:
            recorder.process_input(input_=input_)
        assert recorder.state == "27710581,27710631"

    def test_recorder_value_too_wide(self):
        recorder = UsageRecorder()
        for input_ in [
            get_timed_input(minutes=-14),
            get_timed_input(minutes=-1),
        ]:
            recorder.process_input(input_=input_)

        with pytest.raises(TooWideUsageError):
            recorder.process_input(input_=get_timed_input(minutes=52))

        assert recorder.value == 20

    def test_recorder_value_from_state(self):
        recorder = UsageRecorder()
        recorder.restore_state("27710581,27710631")
        assert recorder.value == 20

    def test_recorder_value_wrong_input_type(self):
        recorder = UsageRecorder()
        with pytest.raises(WrongInputTypeError):
            recorder.process_input(input_=Input())
