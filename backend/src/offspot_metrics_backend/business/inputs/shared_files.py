from dataclasses import dataclass
from enum import Enum

from offspot_metrics_backend.business.inputs.input import Input


class SharedFilesOperationKind(str, Enum):
    """The various kind of supported aggregations"""

    FILE_CREATED = "FILE_CREATED"
    FILE_DELETED = "FILE_DELETED"


@dataclass
class SharedFilesOperation(Input):
    """Input representing an operation on a shared files software (EduPi for now)"""

    # kind of operation (creation or deletion for now)
    kind: SharedFilesOperationKind
