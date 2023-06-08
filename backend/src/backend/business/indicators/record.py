from dataclasses import dataclass

from backend.business.indicators import DimensionsValues


@dataclass
class Record:
    """Data class holding a record (recorder value with its dimensions values)"""

    value: int
    dimensions: DimensionsValues
