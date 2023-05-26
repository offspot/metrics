import abc

from backend.business.inputs.input import InputInterface


class RecorderInterface(metaclass=abc.ABCMeta):
    """Generic interface to recorder types"""

    @abc.abstractmethod
    def process_input(self, input: InputInterface) -> None:
        """Process an input by updating recorder internal state"""
        raise NotImplementedError  # pragma: nocover

    @abc.abstractmethod
    def get_value(self) -> None:
        """Return the current value of the recorder, based on internal state"""
        raise NotImplementedError  # pragma: nocover


@abc.abstractmethod
class IntCounterRecorder(RecorderInterface):
    """Basic recorder type counting the number of inputs that have been processed"""

    # internal state is simply a counter
    counter: int = 0

    def process_input(self, input: InputInterface) -> None:
        """Processing an input consists simply in updating the counter"""
        self.counter += 1

    def get_value(self) -> None:
        """Retrieving the value consists simply is getting the counter"""
        return self.counter
