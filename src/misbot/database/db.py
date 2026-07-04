from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine

from misbot.config import get_settings

settings = get_settings()

engine = create_async_engine(
    url=settings.database.sqlite_connection_string,
    connect_args={
        "autocommit": False,
    },
    echo=settings.database.sql_echo,
)


# enabling-non-legacy-sqlite-transactional-modes-with-the-sqlite3-or-aiosqlite-driver


@event.listens_for(engine.sync_engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable aiosqlite's emitting of the BEGIN statement entirely.
    dbapi_connection.isolation_level = None
