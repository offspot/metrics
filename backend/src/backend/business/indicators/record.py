from dataclasses import dataclass

from backend.business.indicators import DimensionsValues


@dataclass
class Record:
    """Data class holding a record (recorder value with its dimensions values)"""

    value: int
    dimensions: DimensionsValues

    def get_dimension_value(self, dimension: int) -> str | None:
        return self.dimensions[dimension] if len(self.dimensions) > dimension else None
