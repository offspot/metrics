from typing import Any

import pytest
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.kpis.shared_files import (
    SharedFiles,
    SharedFilesValue,
)


@pytest.fixture
def shared_files_value_as_object_1() -> SharedFilesValue:
    return SharedFilesValue(files_created=0, files_deleted=11)


@pytest.fixture
def shared_files_value_as_object_2() -> SharedFilesValue:
    return SharedFilesValue(files_created=33, files_deleted=11)


@pytest.fixture
def shared_files_value_as_object_3() -> SharedFilesValue:
    return SharedFilesValue(files_created=33, files_deleted=0)


@pytest.fixture
def shared_files_value_as_dict_1() -> dict[str, Any]:
    return {
        "files_created": 0,
        "files_deleted": 11,
    }


def test_shared_files_compute_1(
    shared_files_value_as_object_1: SharedFilesValue,
    shared_files_value_as_dict_1: dict[str, Any],
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = SharedFiles()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=2, stop_ts=3, session=dbsession
    )
    assert value == shared_files_value_as_object_1
    assert SharedFilesValue.model_dump(value) == shared_files_value_as_dict_1


def test_shared_files_compute_2(
    shared_files_value_as_object_2: SharedFilesValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = SharedFiles()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=3, session=dbsession
    )
    assert value == shared_files_value_as_object_2


def test_shared_files_compute_3(
    shared_files_value_as_object_3: SharedFilesValue,
    dbsession: Session,
    kpi_dataset: None,  # noqa: ARG001
):
    kpi = SharedFiles()
    value = kpi.compute_value_from_indicators(
        agg_kind=AggKind.DAY, start_ts=1, stop_ts=1, session=dbsession
    )
    assert value == shared_files_value_as_object_3
