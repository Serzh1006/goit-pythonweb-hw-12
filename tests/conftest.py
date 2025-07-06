import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from src.auth.auth import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.databases.models import Contact

from main import app
from src.databases.models import User
from src.databases.connect import Base, get_db
from src.auth.auth import create_access_token, Hash


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:111111@localhost:5432/test_contacts_db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, class_=AsyncSession, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}

@pytest_asyncio.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                password=hash_password,
                confirmed=True,
                avatar= None,
            )
            session.add(current_user)
            await session.commit()


@pytest_asyncio.fixture()
async def async_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    async def override_get_current_user():
        async with TestingSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == test_user["email"]))
            user = result.scalar_one()
            return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield TestClient(app)

@pytest.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["email"]})
    return token

@pytest.fixture
async def existing_contact_id(async_session):
    result = await async_session.execute(select(Contact).limit(1))
    contact = result.scalars().first()
    assert contact is not None
    return contact.id

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client