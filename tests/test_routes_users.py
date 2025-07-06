import io
import pytest
from fastapi import status, UploadFile
from unittest.mock import AsyncMock, patch
from fastapi.testclient import AsyncClient
from src.databases.models import User
from src.schemas.user import UserOut
from main import app

@pytest.fixture
def test_user():
    return User(id=1, email="test@example.com", avatar=None)

@pytest.mark.asyncio
async def test_me_endpoint(test_user):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email

@pytest.mark.asyncio
@patch("src.services.update_avatar.upload_avatar")
@patch("src.cache_func.user_cache.set_user_to_cache", new_callable=AsyncMock)
async def test_update_avatar_success(mock_set_cache, mock_upload_avatar, test_user):
    mock_upload_avatar.return_value = "http://avatar.url/avatar.jpg"

    file_content = io.BytesIO(b"fake image content")
    upload_file = UploadFile(filename="avatar.png", file=file_content, content_type="image/png")

    class MockDBSession:
        def __init__(self):
            self.committed = False
            self.refreshed = False

        def query(self, model):
            class Query:
                def filter(self_inner, condition):
                    return self_inner
                def first(self_inner):
                    return test_user
            return Query()

        def commit(self):
            self.committed = True

        def refresh(self, user):
            self.refreshed = True

    db = MockDBSession()

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        files = {"file": ("avatar.png", b"fake image content", "image/png")}
        response = await client.post("/users/avatar", files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"avatar_url": "http://avatar.url/avatar.jpg"}

    mock_upload_avatar.assert_called_once()
    mock_set_cache.assert_awaited()

@pytest.mark.asyncio
async def test_update_avatar_fail_invalid_file_type(test_user):
    files = {"file": ("file.txt", b"not an image", "text/plain")}

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/users/avatar", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Файл має бути зображенням"