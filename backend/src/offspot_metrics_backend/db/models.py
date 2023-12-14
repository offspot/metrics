import json
from datetime import datetime
from types import MappingProxyType
from typing import Any, cast

from sqlalchemy import (
    DateTime,
    Dialect,
    ForeignKey,
    Index,
    UniqueConstraint,
    select,
    types,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData

from offspot_metrics_backend.business.indicators.dimensions import DimensionsValues
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.schemas import CamelModel


class KpiValue(CamelModel):
    pass


class SerializedData(CamelModel):
    module: str
    name: str
    data: Any


class KpiValueType(types.TypeDecorator[KpiValue]):
    """Handle KpiValue serialization/deserialization in a transparent way."""

    impl = types.String

    cache_ok = True

    def process_bind_param(
        self,
        value: KpiValue | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> str | None:
        if not value:
            return None  # pragma: no cover (value cannot be null in DB)
        return SerializedData(
            module=value.__class__.__module__,
            name=value.__class__.__name__,
            data=cast(CamelModel, value).model_dump(by_alias=True),
        ).model_dump_json(by_alias=True)

    def process_result_value(
        self,
        value: Any | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> KpiValue | None:
        ser_info = SerializedData.model_validate(json.loads(cast(str, value)))
        clazz: type[KpiValue] | None = None
        for subclass in KpiValue.__subclasses__():
            if (
                subclass.__module__ == ser_info.module
                and subclass.__name__ == ser_info.name
            ):
                clazz = subclass
        if clazz is None:  # pragma: no cover (very difficult to simulate in a test)
            raise ValueError(
                f"Class not found for module {ser_info.module}"
                f" and name {ser_info.name}"
            )
        return cast(KpiValue, cast(CamelModel, clazz).model_validate(ser_info.data))


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
