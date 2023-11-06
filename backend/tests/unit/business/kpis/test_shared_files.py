from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.shared_files import (
    SharedFiles,
    SharedFilesValue,
)

SHARED_FILES_VALUE_AS_OBJECT_1 = SharedFilesValue(files_created=0, files_deleted=11)
SHARED_FILES_VALUE_AS_OBJECT_2 = SharedFilesValue(files_created=33, files_deleted=11)
SHARED_FILES_VALUE_AS_OBJECT_3 = SharedFilesValue(files_created=33, files_deleted=0)

SHARED_FILES_VALUE_AS_DICT_1 = {
    "files_created": 0,
    "files_deleted": 11,
}


def test_shared_files_compute(dbsession: Session, kpi_dataset: None):  # noqa: ARG001
    kpi = SharedFiles()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == SHARED_FILES_VALUE_AS_OBJECT_1
    assert SharedFilesValue.model_dump(value) == SHARED_FILES_VALUE_AS_DICT_1

    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=3, session=dbsession
    )
    assert value == SHARED_FILES_VALUE_AS_OBJECT_2

    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == SHARED_FILES_VALUE_AS_OBJECT_3
