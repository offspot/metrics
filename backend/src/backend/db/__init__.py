from typing import Any, Callable

from sqlalchemy import SelectBase, create_engine, event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from backend.constants import BackendConf

Session = sessionmaker(bind=create_engine(url=BackendConf.database_url, echo=False))


# Enable foreign_keys management on all connections
# See https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: DBAPIConnection, connection_record: ConnectionPoolEntry
):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def dbsession(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to create an SQLAlchemy ORM session object and wrap the function
    inside the session. A `session` argument is automatically set. Commit is
    automatically performed when the function finish (and before returning to
    the caller). Should any exception arise, rollback of the transaction is also
    automatic.
    """

    def inner(*args: Any, **kwargs: Any) -> Any:
        with Session.begin() as session:
            kwargs["session"] = session
            return func(*args, **kwargs)

    return inner


def count_from_stmt(session: OrmSession, stmt: SelectBase) -> int:
    """Count all records returned by any statement `stmt` passed as parameter"""
    return session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
