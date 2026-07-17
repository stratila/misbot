import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from misbot.database.models import users


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user in the database."""
    stmt = users.insert().values(is_admin=True)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = select(users).where(users.c.is_admin == True)  # noqa: E712
    result = await db_session.execute(stmt)
    user = result.first()
    assert user is not None
    assert user.is_admin is True

    # cleanup
    await db_session.execute(users.delete())
    await db_session.commit()


@pytest.mark.asyncio
async def test_query_nonexistent_user(db_session: AsyncSession):
    """Test querying a user that does not exist."""
    stmt = select(users).where(users.c.id == 9999)
    result = await db_session.execute(stmt)
    user = result.first()
    assert user is None
    # table is empty, no cleanup needed


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test updating a user in the database."""
    stmt = users.insert().values(is_admin=False)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = users.update().where(users.c.is_admin == False).values(is_admin=True)  # noqa: E712
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = select(users).where(users.c.is_admin == True)  # noqa: E712
    result = await db_session.execute(stmt)
    user = result.first()
    assert user is not None
    assert user.is_admin is True

    # cleanup
    await db_session.execute(users.delete())
    await db_session.commit()


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test deleting a user from the database."""
    stmt = users.insert().values(is_admin=False)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = users.delete().where(users.c.is_admin == False)  # noqa: E712
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = select(users).where(users.c.is_admin == False)  # noqa: E712
    result = await db_session.execute(stmt)
    user = result.first()
    assert user is None

    # cleanup just in case
    await db_session.execute(users.delete())
    await db_session.commit()


@pytest.mark.asyncio
async def test_multiple_users(db_session: AsyncSession):
    """Test inserting and querying multiple users."""
    stmt = users.insert().values(is_admin=False)
    await db_session.execute(stmt)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = select(users)
    result = await db_session.execute(stmt)
    all_users = result.fetchall()
    assert len(all_users) == 2

    # cleanup
    await db_session.execute(users.delete())
    await db_session.commit()


@pytest.mark.asyncio
async def test_user_uniqueness(db_session: AsyncSession):
    """Test that user IDs are unique."""
    stmt = users.insert().values(is_admin=False)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = users.insert().values(is_admin=False)
    await db_session.execute(stmt)
    await db_session.commit()

    stmt = select(users)
    result = await db_session.execute(stmt)
    all_users = result.fetchall()
    assert len(all_users) == 2
    assert all_users[0].id != all_users[1].id

    # cleanup
    await db_session.execute(users.delete())
    await db_session.commit()
