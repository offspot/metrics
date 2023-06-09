from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData


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
    __tablename__ = "indicator_period"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    day: Mapped[int]
    weekday: Mapped[int]
    hour: Mapped[int]


class IndicatorDimension(Base):
    __tablename__ = "indicator_dimension"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    # only 3 dimension values are supported for now, this is supposed to be way enough
    value0: Mapped[Optional[str]]
    value1: Mapped[Optional[str]]
    value2: Mapped[Optional[str]]


class IndicatorRecord(Base):
    __tablename__ = "indicator_record"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(index=True)
    value: Mapped[int]

    period_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_period.id"), init=False
    )

    period: Mapped["IndicatorPeriod"] = relationship(init=False)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)
