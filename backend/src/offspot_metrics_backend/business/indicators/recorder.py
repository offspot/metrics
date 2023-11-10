import abc
import datetime
import math

from offspot_metrics_backend.business.exceptions import (
    TooWideUsageError,
    WrongInputTypeError,
)
from offspot_metrics_backend.business.inputs.input import Input, TimedInput


class Recorder(abc.ABC):
    """Generic interface to recorder types"""

    @abc.abstractmethod
    def process_input(self, input_: Input) -> None:
        """Process an input by updating recorder internal state"""
        ...  # pragma: no cover

    @property
    @abc.abstractmethod
    def value(self) -> int:
        """Return the final value of the recorder, based on internal state"""
        ...  # pragma: no cover

    @property
    @abc.abstractmethod
    def state(self) -> str:
        """Return a serialized representation of recorder internal state"""
        ...  # pragma: no cover

    @abc.abstractmethod
    def restore_state(self, value: str):
        """Restore the recorder internal state from its serialized representation"""
        ...  # pragma: no cover


class IntCounterRecorder(Recorder):
    """Basic recorder type counting the number of inputs that have been processed"""

    def __init__(self) -> None:
        self.counter: int = 0

    def process_input(
        self,
        input_: Input,  # noqa: ARG002
    ) -> None:
        """Processing an input consists simply in updating the counter"""
        self.counter += 1

    @property
    def value(self) -> int:
        """Retrieving the value consists simply is getting the counter"""
        return self.counter

    @property
    def state(self) -> str:
        """Return a serialized representation of recorder internal state"""
        return f"{self.counter}"

    def restore_state(self, value: str):
        """Restore the recorder internal state from its serialized representation"""
        self.counter = int(value)


class UsageRecorder(Recorder):
    """Recorder counting the number of minutes of activity using slots

    If any input is received during a slot (10 minutes), the slot is marked as active.
    The final value is the count of all active slots multiplied by the slot duration.
    """

    slot_duration = 10
    max_active_intervals = 6
    max_time_range = 62

    def __init__(self) -> None:
        self.active_interval_starts: list[int] = []

    def _format_minutes(self, minutes: int) -> str:
        """Transform a value in minutes into a nice datetime in ISO format"""
        return datetime.datetime.fromtimestamp(minutes * 60).isoformat()

    def process_input(
        self,
        input_: Input,
    ) -> None:
        """Processing an input consists in updating active starts list"""
        if not isinstance(input_, TimedInput):
            raise WrongInputTypeError(
                f"{UsageRecorder.__name__} recorder can only process "
                f"{TimedInput.__name__} inputs"
            )
        active_minute = math.floor(input_.ts.timestamp() / 60)

        if not self.active_interval_starts:
            # If there are no active intervals yet, use the current minute
            active_interval_start = active_minute
        else:
            # Check for TooWideUsageError
            time_range = active_minute - self.active_interval_starts[0]
            if time_range > self.max_time_range:
                raise TooWideUsageError(
                    f"Time range is too big ({time_range} mins from"
                    f" {self._format_minutes(self.active_interval_starts[0])} to"
                    f" {self._format_minutes(active_minute)})"
                )

            if time_range >= self.max_active_intervals * self.slot_duration:
                # When input happened just after the max active intervals, calculate
                # the start time of the last possible interval aligned to slot_duration
                active_interval_start = self.active_interval_starts[
                    0
                ] + self.slot_duration * (self.max_active_intervals - 1)
            else:
                # Calculate the start time of the next interval aligned to
                # slot_duration
                active_interval_start = (
                    active_minute
                    - (active_minute - self.active_interval_starts[0])
                    % self.slot_duration
                )

        # Check if the interval already exists in the list
        if active_interval_start not in self.active_interval_starts:
            # Add the start time of the new interval
            self.active_interval_starts.append(active_interval_start)

    @property
    def value(self) -> int:
        """Retrieving the value consists in counting active slots"""
        return self.slot_duration * len(self.active_interval_starts)

    @property
    def state(self) -> str:
        """Return a serialized representation of recorder internal state"""
        return f"{','.join([str(start) for start in self.active_interval_starts])}"

    def restore_state(self, value: str):
        """Restore the recorder internal state from its serialized representation"""
        self.active_interval_starts = [int(start) for start in value.split(",")]
