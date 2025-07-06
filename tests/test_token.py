import pytest
from jose import jwt
from datetime import datetime, timedelta
from src.services.email_token import create_email_token, decode_email_token
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

@pytest.mark.asyncio
async def test_create_email_token_returns_string():
    data = {"sub": "test@example.com"}
    token = await create_email_token(data)
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_decode_email_token_valid():
    data = {"sub": "test@example.com"}
    token = await create_email_token(data)
    sub = await decode_email_token(token)
    assert sub == data["sub"]

@pytest.mark.asyncio
async def test_decode_email_token_invalid():
    invalid_token = "this.is.not.a.valid.token"
    sub = await decode_email_token(invalid_token)
    assert sub is None

@pytest.mark.asyncio
async def test_decode_email_token_expired():
    expired_payload = {"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(hours=1)}
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    sub = await decode_email_token(expired_token)
    assert sub is None