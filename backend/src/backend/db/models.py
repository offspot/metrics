from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData

from backend.business.indicators.dimensions import DimensionsValues
from backend.business.period import Period


class Base(MappedAsDataclass, DeclarativeBase):
    # This map details the specific transformation of types between Python and
    # SQLite. This is only needed for the case where a specific SQLite
    # type has to be used or when we want to ensure a specific setting (like the
    # timezone below)
    type_annotation_map = {
        datetime: DateTime(
            timezone=False
        ),  # transform Python datetime into SQLAlchemy Datetime without timezone
    }

    # This metadata specifies some naming conventions that will be used by
    # alembic to generate constraints names (indexes, unique constraints, ...)
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    pass


class IndicatorPeriod(Base):
    """An indicator period, i.e. a given hour on a given day"""

    __tablename__ = "indicator_period"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    day: Mapped[int]
    weekday: Mapped[int]
    hour: Mapped[int]
    timestamp: Mapped[int]

    __table_args__ = (UniqueConstraint("year", "month", "day", "hour"),)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "IndicatorPeriod":
        """Transform datetime to DB object"""
        return cls.from_period(Period(dt))

    @classmethod
    def from_period(cls, period: Period) -> "IndicatorPeriod":
        """Transform business period object to DB object"""
        return cls(
            year=period.year,
            month=period.month,
            day=period.day,
            weekday=period.weekday,
            hour=period.hour,
            timestamp=period.timestamp,
        )

    @classmethod
    def get_from_db_or_none(
        cls, period: Period, session: Session
    ) -> "IndicatorPeriod | None":
        """Search for a period in DB based on business object"""
        return session.execute(
            select(IndicatorPeriod)
            .where(IndicatorPeriod.year == period.year)
            .where(IndicatorPeriod.month == period.month)
            .where(IndicatorPeriod.day == period.day)
            .where(IndicatorPeriod.hour == period.hour)
        ).scalar_one_or_none()

    def to_period(self) -> Period:
        """Transform this DB object into business object"""
        return Period(
            datetime.fromisoformat(
                f"{self.year:04}-{self.month:02}-{self.day:02} {self.hour:02}:00:00"
            )
        )


class IndicatorDimension(Base):
    """An indicator dimension

    A dimension is the value of an indicator (e.g. a content name).
    It might have up to 3 values for now, meaning a 3 dimensional indicator"""

    __tablename__ = "indicator_dimension"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    # only 3 dimension values are supported for now, this is supposed to be way enough
    value0: Mapped[Optional[str]] = mapped_column(index=True)
    value1: Mapped[Optional[str]]
    value2: Mapped[Optional[str]]

    def to_values(self) -> DimensionsValues:
        return DimensionsValues(self.value0, self.value1, self.value2)


class IndicatorRecord(Base):
    """An indicator record

    A record is the value of a given indicator on a given period for a given dimension
    """

    __tablename__ = "indicator_record"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(index=True)
    value: Mapped[int]

    period_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_period.id"), init=False, index=True
    )

    period: Mapped["IndicatorPeriod"] = relationship(init=False)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)

    __table_args__ = (UniqueConstraint("indicator_id", "period_id", "dimension_id"),)


class IndicatorState(Base):
    """An indicator temporary state

    The state is a temporary value used by the indicator while still in memory and
    before the end of the period where the state is transformed into a record
    """

    __tablename__ = "indicator_state"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(index=True)
    state: Mapped[str]

    period_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_period.id"), init=False
    )

    period: Mapped["IndicatorPeriod"] = relationship(init=False)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)

    __table_args__ = (UniqueConstraint("indicator_id", "period_id", "dimension_id"),)


class KpiValue(Base):
    """The value of a KPI of a given aggregation kind and value

    The kind of aggregration is either D (day), W (week), M (month) or Y (year)"""

    __tablename__ = "kpi"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    kpi_id: Mapped[int] = mapped_column(index=True)
    agg_kind: Mapped[str]
    agg_value: Mapped[str]
    kpi_value: Mapped[str]

    __table_args__ = (
        UniqueConstraint("kpi_id", "agg_value"),
        Index("kpi_id", "agg_kind"),
    )
