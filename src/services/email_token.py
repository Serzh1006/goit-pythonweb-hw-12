from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


async def create_email_token(data: dict):
    """
    Создает JWT токен для подтверждения email с временем жизни 1 час.

    Args:
        data (dict): Данные для кодирования в токен (например, {"sub": email}).

    Returns:
        str: Закодированный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def decode_email_token(token: str):
    """
    Декодирует JWT токен и извлекает значение поля 'sub' (например, email).

    Args:
        token (str): JWT токен для декодирования.

    Returns:
        str | None: Значение поля 'sub', если токен валиден, иначе None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None
