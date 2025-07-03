import pytest
from src.databases.models import User
from src.repository.users import authenticate_user
from src.auth.auth import Hash
from sqlalchemy import text

@pytest.mark.asyncio
async def test_authenticate_user_success(async_session):
    await async_session.execute(text("DELETE FROM users WHERE username = 'testuser'"))
    await async_session.commit()
    user = User(
        username="testuser",
        email="test@example.com",
        password=Hash().get_password_hash("password123"),
        confirmed=True
    )
    async_session.add(user)
    await async_session.commit()

    auth_user = await authenticate_user("test@example.com", "password123", async_session)
    assert auth_user is not None
    assert auth_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_authenticate_user_failure_wrong_password(async_session):
    user = User(
        username="testuser2",
        email="fail@example.com",
        password=Hash().get_password_hash("correct_password"),
        confirmed=True
    )
    async_session.add(user)
    await async_session.commit()

    auth_user = await authenticate_user("fail@example.com", "wrong_password", async_session)
    assert auth_user is None

@pytest.mark.asyncio
async def test_authenticate_user_failure_no_user(async_session):
    auth_user = await authenticate_user("nouser@example.com", "any_password", async_session)
    assert auth_user is None