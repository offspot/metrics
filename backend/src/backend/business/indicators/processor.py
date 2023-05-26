from typing import List

from backend.business.indicators.indicator import IndicatorInterface
from backend.business.inputs.input import InputInterface


class Processor:
    """A processor is responsible transform inputs into indicator records"""

    indicators: List[IndicatorInterface] = []

    def process_input(self, input: InputInterface) -> None:
        """Update all indicators for a given input"""
        for indicator in self.indicators:
            indicator.process_input(input=input)

    def reset_state(self) -> None:
        """Reset all indicators"""
        for indicator in self.indicators:
            indicator.reset_state()
