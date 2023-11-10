from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import TimedInput


@dataclass(eq=True, frozen=True)
class ClockTick(TimedInput):
    """Input representing a clock tick ; there is one tick per minute"""
