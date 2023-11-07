from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import InputWithTime


@dataclass
class ClockTick(InputWithTime):
    """Input representing a clock tick ; there is one tick per minute"""
