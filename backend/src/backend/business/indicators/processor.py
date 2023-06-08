from typing import List

from backend.business.indicators.indicator import Indicator
from backend.business.inputs.input import Input


class Processor:
    """A processor is responsible for transforming inputs into indicator records"""

    indicators: List[Indicator] = []

    def process_input(self, input: Input) -> None:
        """Update all indicators for a given input"""
        for indicator in self.indicators:
            indicator.process_input(input=input)

    def reset_state(self) -> None:
        """Reset all indicators"""
        for indicator in self.indicators:
            indicator.reset_state()
