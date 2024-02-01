import abc
import datetime
import math

from offspot_metrics_backend.business.exceptions import (
    TooWideUsageError,
    WrongInputTypeError,
)
from offspot_metrics_backend.business.inputs.input import (
    CountInput,
    Input,
    TimedInput,
)


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


class CountCounterRecorder(Recorder):
    """Basic recorder type suming the number of items reported in input `count`"""

    def __init__(self) -> None:
        self.counter: int = 0

    def process_input(
        self,
        input_: Input,
    ) -> None:
        """Processing an input consists simply in summing the input values"""

        # first check that the recorder is only receiving TimedInputWithCount (should
        # always be the case due to Indicators configuration, but better safe with a
        # clear exception)
        if not isinstance(input_, CountInput):
            raise WrongInputTypeError(
                f"{UsageRecorder.__name__} recorder can only process "
                f"{CountInput.__name__} inputs"
            )

        self.counter += input_.count

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

    # We count activity per 10 minutes (slot_duration).
    # We do not expect to have more than 6 active slots per period (max_active_slots),
    # since otherwise we would be able to report that the thing has been active during
    # 70 minutes out of 60.
    # We allow to receive activity in a single period for up to 62 minutes
    # (max_time_range) between the first activity and the last one. This is meant to
    # cope with the fact that we might receive events either a bit late (due to delays
    # in the processing of logs) or still in the previous period (period switching did
    # not yet occured) ; events received after the 60 minutes of the period are
    # assigned to the last slot (again to not have 7 active slots per hour).
    slot_duration = 10
    max_active_slots = 6
    max_time_range = 62

    def __init__(self) -> None:
        self.active_slots_starts: list[int] = []

    @staticmethod
    def _format_minutes(minutes: int) -> str:
        """Transform a value in minutes into a nice datetime in ISO format"""
        return datetime.datetime.fromtimestamp(minutes * 60).isoformat()

    def process_input(
        self,
        input_: Input,
    ) -> None:
        """Everytime an input is received, mark the corresponding slot as active

        When an input is received, we need to find the corresponding slot and mark it
        as active.

        We do not align slot at 0, 10, 20 ... minutes of the hour, we align
        them with the first input received. I.e. if first input is received at 9
        minutes, the slots will start at 9, 19, 29, ... minutes. This is meant to avoid
        counting two slots if there is only 2 minutes of activity during the hour but
        from 9 to 11 minutes for instance, which would be a bit wrong. We still keep
        slots aligned for simplicity. E.g. if we have activity from 9 to 11 and then
        from 26 to 30 and that's all, we still count 3 slots as active (9 to 18, 19 to
        28 and 29 to 38).

        For keeping a record of which slots are active, we simplify store the list of
        the start minutes of each active slots since this is sufficient data.
        """

        # first check that the recorder is only receiving TimedInput (should always
        # be the case due to Indicators configuration, but better safe with a clear
        # exception)
        if not isinstance(input_, TimedInput):
            raise WrongInputTypeError(
                f"{UsageRecorder.__name__} recorder can only process "
                f"{TimedInput.__name__} inputs"
            )
        active_minute = math.floor(input_.ts.timestamp() / 60)

        if not self.active_slots_starts:
            # If there are no active intervals yet, use the current minute
            active_slot_start = active_minute
        else:
            # Check for TooWideUsageError
            time_range = active_minute - self.active_slots_starts[0]
            if time_range > self.max_time_range:
                raise TooWideUsageError(
                    f"Time range is too big ({time_range} mins from"
                    f" {UsageRecorder._format_minutes(self.active_slots_starts[0])} to"
                    f" {UsageRecorder._format_minutes(active_minute)})"
                )

            if time_range >= self.max_active_slots * self.slot_duration:
                # When input happened just after the max active intervals, calculate
                # the start time of the last possible interval aligned to slot_duration
                active_slot_start = self.active_slots_starts[0] + self.slot_duration * (
                    self.max_active_slots - 1
                )
            else:
                # Calculate the start time of the next interval aligned to
                # slot_duration
                active_slot_start = (
                    active_minute
                    - (active_minute - self.active_slots_starts[0]) % self.slot_duration
                )

        # Check if the interval already exists in the list
        if active_slot_start not in self.active_slots_starts:
            # Add the start time of the new interval
            self.active_slots_starts.append(active_slot_start)

    @property
    def value(self) -> int:
        """Retrieving the value consists in counting active slots"""
        return self.slot_duration * len(self.active_slots_starts)

    @property
    def state(self) -> str:
        """Return a serialized representation of recorder internal state"""
        return f"{','.join([str(start) for start in self.active_slots_starts])}"

    def restore_state(self, value: str):
        """Restore the recorder internal state from its serialized representation"""
        self.active_slots_starts = [int(start) for start in value.split(",")]
