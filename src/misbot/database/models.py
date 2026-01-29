from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
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
    Column("id", String, primary_key=True),
    Column("seen", DateTime, nullable=False),
)

time_spent = Table(
    "time_spent",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("player_id", String, ForeignKey("players.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("duration", Integer, nullable=False),
)
