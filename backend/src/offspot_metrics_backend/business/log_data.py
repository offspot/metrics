import datetime

from pydantic.dataclasses import dataclass


@dataclass
class LogData:
    """Generic log dataclass holding data found in a log line

    This is typically generated from a reverse proxy, but is meant to make
    this independant of the reverse proxy really used"""

    content_type: str | None
    status: int
    uri: str
    method: str
    ts: datetime.datetime
