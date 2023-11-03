import datetime
from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import Input


@dataclass
class ClockTick(Input):
    """Input representing a clock tick ; there is one tick per minute"""

    # moment where the tick occured
    now: datetime.datetime
