from dataclasses import dataclass
from typing import Tuple


@dataclass
class Record:
    """Data class holding a record (recorder value with its dimensions values)"""

    value: int
    dimensions: Tuple[str]
