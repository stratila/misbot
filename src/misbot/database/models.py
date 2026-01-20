from sqlalchemy import Boolean, Column, Integer, Table
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
)
