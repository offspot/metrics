import abc

from offspot_metrics_backend.business.inputs.input import Input


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
        """Return a serialized representation of recorder internal state"""
        self.counter = int(value)
