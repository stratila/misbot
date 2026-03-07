from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Uuid,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

users = Table(
    "users",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("is_admin", Boolean, nullable=False, default=False),
)


channels = Table(
    "channels",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("is_managed", Boolean, nullable=False, default=False),
    Column("status", String, nullable=True),
)


players = Table(
    "players",
    Base.metadata,
    Column("id", Uuid(), primary_key=True),
    Column("seen", DateTime, nullable=False),
)

time_sessions = Table(
    "time_sessions",
    Base.metadata,
    Column("session_id", Uuid(), primary_key=True),
    Column("player_id", Uuid(), ForeignKey("players.id"), nullable=False),
    Column("joined_at", DateTime, nullable=True),
    Column("quit_at", DateTime, nullable=True),
)
