import abc
from typing import Dict, Generator, Tuple

from backend.business.indicators.record import Record
from backend.business.indicators.recorder import RecorderInterface
from backend.business.inputs.input import InputInterface


class IndicatorInterface(metaclass=abc.ABCMeta):
    """A generic indicator interface

    An indicator process one input to update a recorder. If the recorder does not yet
    exists, it is created. An indicator has 0 to n dimensions, depending on the
    indicator implementation. A recorder has an internal state with will allow to
    compute a record, i.e. a value for the associated dimensions values, typically for
    a given processing period.
    """

    _recorders: Dict[Tuple[str], RecorderInterface]

    def __init__(self) -> None:
        self.reset_state()
        super().__init__()

    @abc.abstractmethod
    def can_process_input(self, input: InputInterface) -> bool:
        """Indicates if this indicator can process a given kind of input"""
        raise NotImplementedError  # pragma: nocover

    @abc.abstractmethod
    def get_dimensions_values(self, input: InputInterface) -> Tuple[str]:
        """For a given input (which can be processed), returns the values of each
        indicator dimensions as a tuple (or an empty tuple)."""
        raise NotImplementedError  # pragma: nocover

    @abc.abstractmethod
    def create_new_recorder(self) -> RecorderInterface:
        """Creates a new recorder of appropriate type.

        Appropriate record type depends on the indicator implementation.
        """
        raise NotImplementedError  # pragma: nocover

    def get_or_create_recorder(self, input: InputInterface) -> RecorderInterface:
        """Get or create a recorder whose dimensions are matching the given input.

        Either return the already existing recorder whose dimensions values are
        matching, or creates a new recorder with appropriate dimension values"""
        dimensions_values = self.get_dimensions_values(input)
        if dimensions_values not in self._recorders:
            self._recorders[dimensions_values] = self.create_new_recorder()
        return self._recorders[dimensions_values]

    def reset_state(self):
        """Reset the list of recorders.

        This is typically done at the start of a new processing period"""
        self._recorders = {}

    def get_records(
        self,
    ) -> Generator[Record, None, None]:
        """Return all records (values with associated dimensions)."""
        for dimensions_values, record in self._recorders.items():
            yield Record(value=record.get_value(), dimensions=dimensions_values)

    def process_input(self, input: InputInterface) -> None:
        """Process a given input event

        First, check that the input can be processed by indicator
        Second, retrieve the recorder matching the input
        Third, update the recorder internal state
        """
        if not self.can_process_input(input):
            return
        record = self.get_or_create_recorder(input)
        record.process_input(input)
