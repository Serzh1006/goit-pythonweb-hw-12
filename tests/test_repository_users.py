import pytest
from src.schemas.user import UserCreate
from src.repository.users import create_user
from src.databases.models import User
from tests.conftest import TestingSessionLocal

@pytest.mark.asyncio
async def test_create_user_success():
    user_data = UserCreate(
        username="hulk",
        email="hulk@example.com",
        password="smash123",
        role="user"
    )

    async with TestingSessionLocal() as session:
        user = await create_user(user_data, session)

        assert user.email == user_data.email
        assert user.username == user_data.username
        assert user.role == "user"
        assert user.password != "smash123"