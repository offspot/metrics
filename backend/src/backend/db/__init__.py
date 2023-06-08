from typing import Any, Callable

from sqlalchemy import SelectBase, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session as OrmSession

from backend.constants import BackendConf

AsyncSession = async_sessionmaker(
    bind=create_async_engine(url=BackendConf.database_url, echo=False)
)


def dbsession(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to create an SQLAlchemy ORM session object and wrap the function
    inside the session. A `session` argument is automatically set. Commit is
    automatically performed when the function finish (and before returning to
    the caller). Should any exception arise, rollback of the transaction is also
    automatic.
    """

    async def inner(*args: Any, **kwargs: Any) -> Any:
        async with AsyncSession.begin() as session:
            kwargs["session"] = session
            await func(*args, **kwargs)

    return inner


def count_from_stmt(session: OrmSession, stmt: SelectBase) -> int:
    """Count all records returned by any statement `stmt` passed as parameter"""
    return session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
