import abc

from backend.business.inputs.input import Input


class Recorder(abc.ABC):
    """Generic interface to recorder types"""

    @abc.abstractmethod
    def process_input(self, input: Input) -> None:
        """Process an input by updating recorder internal state"""
        ...  # pragma: nocover

    @abc.abstractmethod
    def get_value(self) -> int:
        """Return the current value of the recorder, based on internal state"""
        ...  # pragma: nocover


class IntCounterRecorder(Recorder):
    """Basic recorder type counting the number of inputs that have been processed"""

    def __init__(self) -> None:
        self.counter = 0

    def process_input(self, input: Input) -> None:
        """Processing an input consists simply in updating the counter"""
        self.counter += 1

    def get_value(self) -> int:
        """Retrieving the value consists simply is getting the counter"""
        return self.counter
