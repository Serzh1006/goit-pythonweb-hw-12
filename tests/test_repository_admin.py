import pytest
from fastapi import HTTPException, status
from fastapi.params import Depends
from src.repository.users import admin_required

class User:
    def __init__(self, role):
        self.role = role


async def override_get_current_user_admin():
    return User(role="admin")

async def override_get_current_user_non_admin():
    return User(role="user")

@pytest.mark.asyncio
async def test_admin_required_allows_admin():
    user = await admin_required(current_user=await override_get_current_user_admin())
    assert user.role == "admin"

@pytest.mark.asyncio
async def test_admin_required_blocks_non_admin():
    with pytest.raises(HTTPException) as exc_info:
        await admin_required(current_user=await override_get_current_user_non_admin())
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Admin access required"