from datetime import datetime
from types import MappingProxyType
from typing import Any, cast
import json
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    select,
    Dialect,
)
from sqlalchemy import types
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData
from marshmallow_dataclass import class_schema as schema

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.period import Period
from dataclasses import dataclass


@dataclass
class KpiValue:
    pass


@dataclass
class DummyKpiValue(KpiValue):
    dummy: str

    def __lt__(self, other: "DummyKpiValue") -> bool:
        return self.dummy < other.dummy


@dataclass
class SerInfo:
    module_name: str
    class_name: str
    ser_value: str


class KpiValueType(types.TypeDecorator[KpiValue]):
    """Handle KpiValue serialization/deserialization in a transparent way."""

    impl = types.String

    cache_ok = True

    def process_bind_param(
        self, value: KpiValue | None, dialect: Dialect
    ) -> str | None:
        if not value:
            return None
        return json.dumps(
            {
                "module_name": value.__class__.__module__,
                "class_name": value.__class__.__name__,
                "serialized": json.loads(
                    cast(
                        str,
                        schema(
                            value.__class__
                        )().dumps(  # pyright: ignore[reportUnknownMemberType]
                            value,
                            many=False,
                        ),
                    )
                ),
            }
        )

    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> KpiValue | None:
        value_str = cast(str, value)
        value_dict = json.loads(value_str)
        clazz: type[KpiValue] | None = None
        for subclass in KpiValue.__subclasses__():
            if (
                subclass.__module__ == value_dict["module_name"]
                and subclass.__name__ == value_dict["class_name"]
            ):
                clazz = subclass
        if clazz is None:
            raise ValueError(
                f"Class not found for module {value_dict['module_name']} and class {value_dict['class_name']}"
            )
        else:
            return schema(clazz)().loads(  # pyright: ignore[reportUnknownMemberType]
                cast(str, json.dumps(value_dict["serialized"])), many=False
            )


class Base(MappedAsDataclass, DeclarativeBase):
    # This map details the specific transformation of types between Python and
    # SQLite. This is only needed for the case where a specific SQLite
    # type has to be used or when we want to ensure a specific setting (like the
    # timezone below). It uses a MappingProxyType to make the dict immutable and
    # avoid strange side-effects (RUF012)
    type_annotation_map = MappingProxyType(
        {
            datetime: DateTime(
                timezone=False
            ),  # transform Python datetime into SQLAlchemy Datetime without timezone
            # KpiValue: String,
            KpiValue: KpiValueType,
        }
    )

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
    timestamp: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "IndicatorPeriod":
        """Transform datetime to DB object"""
        return cls.from_period(Period(dt))

    @classmethod
    def from_period(cls, period: Period) -> "IndicatorPeriod":
        """Transform business period object to DB object"""
        return cls(
            timestamp=period.timestamp,
        )

    @classmethod
    def get_or_none(cls, period: Period, session: Session) -> "IndicatorPeriod | None":
        """Search for a period in DB based on business object"""
        return session.execute(
            select(IndicatorPeriod).where(IndicatorPeriod.timestamp == period.timestamp)
        ).scalar_one_or_none()

    def to_period(self) -> Period:
        """Transform this DB object into business object"""
        return Period.from_timestamp(self.timestamp)


class IndicatorDimension(Base):
    """An indicator dimension

    A dimension is the value of an indicator (e.g. a content name).
    It might have up to 3 values for now, meaning a 3 dimensional indicator"""

    __tablename__ = "indicator_dimension"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # noqa: A003
    # only 3 dimension values are supported for now, this is supposed to be way enough
    value0: Mapped[str | None] = mapped_column(index=True)
    value1: Mapped[str | None]
    value2: Mapped[str | None]

    def to_values(self) -> DimensionsValues:
        return DimensionsValues(self.value0, self.value1, self.value2)


class IndicatorRecord(Base):
    """An indicator record

    A record is the value of a given indicator on a given period for a given dimension
    """

    __tablename__ = "indicator_record"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # noqa: A003
    indicator_id: Mapped[int] = mapped_column(index=True)
    value: Mapped[int]

    period_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_period.timestamp"), init=False, index=True
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
    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # noqa: A003
    indicator_id: Mapped[int] = mapped_column(index=True)
    state: Mapped[str]

    period_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_period.timestamp"), init=False
    )

    period: Mapped["IndicatorPeriod"] = relationship(init=False)

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("indicator_dimension.id"), init=False
    )

    dimension: Mapped["IndicatorDimension"] = relationship(init=False)

    __table_args__ = (UniqueConstraint("indicator_id", "period_id", "dimension_id"),)


class KpiRecord(Base):
    """The value of a KPI of a given aggregation kind and value

    The kind of aggregration is either D (day), W (week), M (month) or Y (year)"""

    __tablename__ = "kpi"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # noqa: A003
    kpi_id: Mapped[int] = mapped_column(index=True)
    agg_kind: Mapped[str]
    agg_value: Mapped[str]
    kpi_value: Mapped[KpiValue]

    __table_args__ = (
        UniqueConstraint("kpi_id", "agg_value"),
        Index("kpi_id", "agg_kind"),
    )
