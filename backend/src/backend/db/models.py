from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData

from backend.business.indicators import DimensionsValues
from backend.business.indicators.period import Period


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

    __table_args__ = (UniqueConstraint("year", "month", "day", "hour"),)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "IndicatorPeriod":
        return cls.from_period(Period(dt))

    @classmethod
    def from_period(cls, period: Period) -> "IndicatorPeriod":
        return cls(
            year=period.year,
            month=period.month,
            day=period.day,
            weekday=period.weekday,
            hour=period.hour,
        )

    @classmethod
    def get_from_db_or_none(
        cls, period: Period, session: Session
    ) -> "IndicatorPeriod | None":
        return session.execute(
            select(IndicatorPeriod)
            .where(IndicatorPeriod.year == period.year)
            .where(IndicatorPeriod.month == period.month)
            .where(IndicatorPeriod.day == period.day)
            .where(IndicatorPeriod.hour == period.hour)
        ).scalar_one_or_none()

    def to_period(self) -> Period:
        return Period(
            datetime.fromisoformat(
                f"{self.year:04}-{self.month:02}-{self.day:02} {self.hour:02}:00:00"
            )
        )


class IndicatorDimension(Base):
    __tablename__ = "indicator_dimension"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    # only 3 dimension values are supported for now, this is supposed to be way enough
    value0: Mapped[Optional[str]]
    value1: Mapped[Optional[str]]
    value2: Mapped[Optional[str]]

    def to_values(self) -> DimensionsValues:
        if self.value0 and self.value1 and self.value2:
            return (self.value0, self.value1, self.value2)
        elif self.value0 and self.value1:
            return (self.value0, self.value1)
        elif self.value0:
            return (self.value0,)
        else:
            return tuple()


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

    __table_args__ = (UniqueConstraint("indicator_id", "period_id", "dimension_id"),)


class IndicatorState(Base):
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
