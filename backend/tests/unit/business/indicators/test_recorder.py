import datetime
from collections.abc import Callable

import pytest
from pydantic.dataclasses import dataclass

from offspot_metrics_backend.business.exceptions import (
    TooWideUsageError,
    WrongInputTypeError,
)
from offspot_metrics_backend.business.indicators.recorder import (
    UsageRecorder,
)
from offspot_metrics_backend.business.inputs.input import Input, TimedInput


@dataclass
class Delay:
    minutes: int = 0
    seconds: int = 0


@pytest.fixture
def start_time() -> datetime.datetime:
    return datetime.datetime.fromisoformat("2022-09-08 11:00:00")


@pytest.fixture
def timed_input(start_time: datetime.datetime) -> Callable[[Delay], TimedInput]:
    def func(delay: Delay) -> TimedInput:
        return TimedInput(
            ts=start_time
            + datetime.timedelta(minutes=delay.minutes, seconds=delay.seconds)
        )

    return func


class TestUsageRecorder:
    @pytest.mark.parametrize(
        "delays, expected_value",
        [
            ([], 0),
            ([Delay()], 10),
            ([Delay(seconds=12)], 10),
            ([Delay(minutes=1, seconds=12)], 10),
            (
                [
                    Delay(),
                    Delay(minutes=1, seconds=12),
                    Delay(minutes=9, seconds=59),
                ],
                10,
            ),
            (
                [
                    Delay(seconds=59),
                    Delay(minutes=1, seconds=12),
                    Delay(minutes=9, seconds=59),
                ],
                10,
            ),
            (
                [Delay(minutes=1), Delay(minutes=10)],
                10,
            ),
            (
                [
                    Delay(seconds=59),
                    Delay(minutes=10),
                ],
                20,
            ),
            (
                [
                    Delay(seconds=59),
                    Delay(minutes=40, seconds=00),
                ],
                20,
            ),
            (
                [
                    Delay(seconds=2),
                    Delay(minutes=40, seconds=00),
                ],
                20,
            ),
            (
                [
                    Delay(seconds=-2),
                    Delay(minutes=8, seconds=00),
                    Delay(minutes=23, seconds=00),
                    Delay(minutes=38, seconds=00),
                    Delay(minutes=40, seconds=00),
                ],
                40,
            ),
            (
                [
                    Delay(seconds=-2),
                    Delay(minutes=8, seconds=00),
                    Delay(minutes=23, seconds=00),
                    Delay(minutes=39, seconds=00),
                    Delay(minutes=40, seconds=00),
                ],
                30,
            ),
            (
                [
                    Delay(seconds=-2),
                    Delay(minutes=59, seconds=30),
                ],
                20,
            ),
            (
                [
                    Delay(seconds=-2),
                    Delay(minutes=10, seconds=00),
                    Delay(minutes=21, seconds=00),
                    Delay(minutes=32, seconds=00),
                    Delay(minutes=43, seconds=00),
                    Delay(minutes=49, seconds=00),
                    Delay(minutes=52, seconds=00),
                ],
                60,
            ),
            (
                [
                    Delay(seconds=-2),
                    Delay(minutes=10, seconds=00),
                    Delay(minutes=21, seconds=00),
                    Delay(minutes=32, seconds=00),
                    Delay(minutes=43, seconds=00),
                    Delay(minutes=49, seconds=00),
                    Delay(minutes=59, seconds=00),
                ],
                60,
            ),
            (
                [
                    Delay(minutes=-14),
                    Delay(minutes=-1),
                ],
                20,
            ),
            (
                [
                    Delay(minutes=-14),
                    Delay(minutes=-1),
                    Delay(minutes=30),
                ],
                30,
            ),
            (
                [
                    Delay(),
                    Delay(minutes=60, seconds=1),
                ],
                20,
            ),
            (
                [
                    Delay(),
                    Delay(minutes=59),
                    Delay(minutes=60, seconds=1),
                ],
                20,
            ),
            (
                [
                    Delay(),
                    Delay(minutes=21),
                    Delay(minutes=59),
                    Delay(minutes=61, seconds=1),
                ],
                30,
            ),
            (
                [
                    Delay(),
                    Delay(minutes=10),
                    Delay(minutes=20),
                    Delay(minutes=30),
                    Delay(minutes=40),
                    Delay(minutes=50),
                    Delay(minutes=59),
                    Delay(minutes=60),
                ],
                60,
            ),
        ],
    )
    def test_recorder_value(
        self,
        timed_input: Callable[[Delay], TimedInput],
        delays: list[Delay],
        expected_value: int,
    ):
        recorder = UsageRecorder()
        for input_ in delays:
            recorder.process_input(input_=timed_input(input_))
        assert recorder.value == expected_value

    def test_recorder_state(self, timed_input: Callable[[Delay], TimedInput]):
        recorder = UsageRecorder()
        for input_ in [
            timed_input(Delay(minutes=1)),
            timed_input(Delay(minutes=1, seconds=12)),
            timed_input(Delay(minutes=52)),
        ]:
            recorder.process_input(input_=input_)
        assert recorder.state == "27710581,27710631"

    def test_recorder_value_too_wide(self, timed_input: Callable[[Delay], TimedInput]):
        recorder = UsageRecorder()
        for input_ in [
            timed_input(Delay(minutes=-14)),
            timed_input(Delay(minutes=-1)),
        ]:
            recorder.process_input(input_=input_)

        with pytest.raises(TooWideUsageError):
            recorder.process_input(input_=timed_input(Delay(minutes=52)))

        assert recorder.value == 20

    def test_recorder_value_from_state(self):
        recorder = UsageRecorder()
        recorder.restore_state("27710581,27710631")
        assert recorder.value == 20

    def test_recorder_value_wrong_input_type(self):
        recorder = UsageRecorder()
        with pytest.raises(WrongInputTypeError):
            recorder.process_input(input_=Input())
