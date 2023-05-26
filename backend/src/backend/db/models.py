from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
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


# class Sample(Base):
#     __tablename__ = "sample"
#     id: Mapped[int] = mapped_column(init=False, primary_key=True)
