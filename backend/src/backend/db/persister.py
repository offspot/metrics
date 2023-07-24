from typing import List, Optional

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from ..business.agg_kind import AggKind
from ..business.indicators.indicator import Indicator
from ..business.kpis.value import Value
from ..business.period import Period
from ..db.models import IndicatorDimension as DimensionDb
from ..db.models import IndicatorRecord as RecordDb
from ..db.models import IndicatorState as StateDb
from ..db.models import KpiValue as KpiValueDb


class Persister:
    @classmethod
    def clear_indicator_states(cls, session: Session) -> None:
        """Delete all indicator states stored in DB"""
        session.execute(sa.delete(StateDb))

    @classmethod
    def persist_indicator_dimensions(
        cls, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all dimensions of all indicators in DB if not already present"""
        for indicator in indicators:
            for record in indicator.get_records():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one_or_none()

                if not dbDimension:
                    dbDimension = DimensionDb(
                        record.dimensions.value0,
                        record.dimensions.value1,
                        record.dimensions.value2,
                    )
                    session.add(dbDimension)

    @classmethod
    def persist_indicator_records(
        cls, period: Period, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all indicator records in DB"""
        for indicator in indicators:
            for record in indicator.get_records():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == record.dimensions.value0)
                    .where(DimensionDb.value1 == record.dimensions.value1)
                    .where(DimensionDb.value2 == record.dimensions.value2)
                ).scalar_one()
                dbRecord = RecordDb(
                    indicator_id=indicator.unique_id,
                    value=record.value,
                    timestamp=period.timestamp,
                )
                dbRecord.dimension = dbDimension
                session.add(dbRecord)

    @classmethod
    def persist_indicator_states(
        cls, period: Period, indicators: List[Indicator], session: Session
    ) -> None:
        """Store all indicators temporary state in DB"""
        for indicator in indicators:
            for state in indicator.get_states():
                dbDimension = session.execute(
                    sa.select(DimensionDb)
                    .where(DimensionDb.value0 == state.dimensions.value0)
                    .where(DimensionDb.value1 == state.dimensions.value1)
                    .where(DimensionDb.value2 == state.dimensions.value2)
                ).scalar_one()
                dbState = StateDb(
                    indicator_id=indicator.unique_id,
                    state=state.value,
                    timestamp=period.timestamp,
                )
                dbState.dimension = dbDimension
                session.add(dbState)

    @classmethod
    def get_last_period(cls, session: Session) -> Optional[Period]:
        """Return the last period stored in DB"""
        stateTimestamp = session.execute(
            sa.select(StateDb.timestamp).order_by(StateDb.timestamp.desc()).limit(1)
        ).scalar_one_or_none()
        recordTimestamp = session.execute(
            sa.select(RecordDb.timestamp).order_by(RecordDb.timestamp.desc()).limit(1)
        ).scalar_one_or_none()
        if stateTimestamp is None:
            if recordTimestamp is None:
                return None
            else:
                return Period.from_timestamp(recordTimestamp)
        else:
            if recordTimestamp is None:
                return Period.from_timestamp(stateTimestamp)
            else:
                return Period.from_timestamp(min(stateTimestamp, recordTimestamp))

    @classmethod
    def get_restore_data(
        cls, period: Period, indicator_id: int, session: Session
    ) -> List[StateDb]:
        """Return all state data to restore from DB to memory"""
        return list(
            session.execute(
                sa.select(StateDb)
                .where(StateDb.indicator_id == indicator_id)
                .where(StateDb.timestamp == period.timestamp)
            ).scalars()
        )

    @classmethod
    def get_kpi_values(
        cls, kpi_id: int, agg_kind: AggKind, session: Session
    ) -> List[Value]:
        """Return all KPI values for a given KPI and a given kind of period"""
        return [
            Value(agg_value=dbValue.agg_value, kpi_value=dbValue.kpi_value)
            for dbValue in session.execute(
                sa.select(KpiValueDb)
                .where(KpiValueDb.kpi_id == kpi_id)
                .where(KpiValueDb.agg_kind == agg_kind.value)
            ).scalars()
        ]

    @classmethod
    def delete_kpi_value(
        cls, kpi_id: int, agg_kind: AggKind, agg_value: str, session: Session
    ) -> None:
        """Delete a KPI value for a given KPI, kind of period and period"""
        session.execute(
            sa.delete(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.agg_kind == agg_kind.value)
            .where(KpiValueDb.agg_value == agg_value)
        )

    @classmethod
    def update_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: AggKind,
        agg_value: str,
        kpi_value: str,
        session: Session,
    ) -> None:
        """Update a KPI value for a given KPI, kind of period and period"""
        obj = session.execute(
            sa.select(KpiValueDb)
            .where(KpiValueDb.kpi_id == kpi_id)
            .where(KpiValueDb.agg_kind == agg_kind.value)
            .where(KpiValueDb.agg_value == agg_value)
        ).scalar_one()
        obj.kpi_value = kpi_value

    @classmethod
    def add_kpi_value(
        cls,
        kpi_id: int,
        agg_kind: AggKind,
        agg_value: str,
        kpi_value: str,
        session: Session,
    ) -> None:
        """Add a KPI value for a given KPI, kind of period and period"""
        session.add(
            KpiValueDb(
                kpi_id=kpi_id,
                agg_kind=agg_kind.value,
                agg_value=agg_value,
                kpi_value=kpi_value,
            )
        )

    @classmethod
    def cleanup_obsolete_data(cls, current_period: Period, session: Session) -> None:
        """Delete obsolete data from DB

        For now, obsolete data is indicators older than 1 year compared to current
        period. Associated unused data (records, states, dimensions) is cleaned as
        well.
        """

        oldest_valid_ts = current_period.get_shifted(relativedelta(years=-1)).timestamp

        # delete records associated with old periods
        session.execute(sa.delete(RecordDb).where(RecordDb.timestamp < oldest_valid_ts))

        # just in case, delete old states associated with old periods (should never
        # be needed, but will avoid DB integrity errors)
        session.execute(sa.delete(StateDb).where(StateDb.timestamp < oldest_valid_ts))

        # delete indicator dimensions that are not used anymore
        session.execute(
            sa.delete(DimensionDb).where(
                DimensionDb.id.not_in(sa.select(RecordDb.dimension_id).distinct())
            )
        )
