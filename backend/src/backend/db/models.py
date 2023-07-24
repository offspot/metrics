from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData

from ..business.indicators.dimensions import DimensionsValues


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
    timestamp: Mapped[int] = mapped_column(index=True)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)

    __table_args__ = (UniqueConstraint("indicator_id", "dimension_id", "timestamp"),)


class IndicatorState(Base):
    """An indicator temporary state

    The state is a temporary value used by the indicator while still in memory and
    before the end of the period where the state is transformed into a record
    """

    __tablename__ = "indicator_state"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(index=True)
    state: Mapped[str]
    timestamp: Mapped[int] = mapped_column(index=True)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)

    __table_args__ = (UniqueConstraint("indicator_id", "dimension_id", "timestamp"),)


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
