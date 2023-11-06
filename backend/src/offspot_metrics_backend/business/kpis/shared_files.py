from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from offspot_metrics_backend.business.agg_kind import AggKind
from offspot_metrics_backend.business.indicators.shared_files import (
    SharedFilesOperations,
)
from offspot_metrics_backend.business.inputs.shared_files import (
    SharedFilesOperationKind,
)
from offspot_metrics_backend.business.kpis.kpi import Kpi
from offspot_metrics_backend.db.models import (
    IndicatorDimension,
    IndicatorPeriod,
    IndicatorRecord,
    KpiValue,
)


class SharedFilesValue(BaseModel, KpiValue):
    files_created: int
    files_deleted: int


class SharedFiles(Kpi):
    """A KPI which measures some statistics about shared files (EduPi for now) usage

    Value is a single measure for the period of files added and files removed
    """

    unique_id = 2005

    def compute_value_from_indicators(
        self,
        agg_kind: AggKind,  # noqa: ARG002
        start_ts: int,
        stop_ts: int,
        session: Session,
    ) -> SharedFilesValue:
        """For a kind of aggregation (daily, weekly, ...) and a given period, return
        the KPI value."""

        counts = session.execute(
            select(
                IndicatorDimension.value0.label("operation"),
                func.sum(IndicatorRecord.value).label("total"),
            )
            .join(IndicatorRecord)
            .join(IndicatorPeriod)
            .where(IndicatorRecord.indicator_id == SharedFilesOperations.unique_id)
            .where(IndicatorPeriod.timestamp >= start_ts)
            .where(IndicatorPeriod.timestamp <= stop_ts)
            .group_by("operation")
        ).all()

        files_created = 0
        files_deleted = 0
        for count_record in counts:
            if count_record.operation == SharedFilesOperationKind.FILE_CREATED:
                files_created = count_record.total
            elif count_record.operation == SharedFilesOperationKind.FILE_DELETED:
                files_deleted = count_record.total
            else:
                # we should never get there except if the enum is modified and we
                # forget to modify this function
                raise AttributeError("Unexpected operation found")  # pragma: no cover

        return SharedFilesValue(
            files_created=files_created, files_deleted=files_deleted
        )
