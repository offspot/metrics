from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import TimedInput


@dataclass
class ClockTick(TimedInput):
    """Input representing a clock tick ; there is one tick per minute"""
