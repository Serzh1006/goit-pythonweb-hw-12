from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from src.databases.connect import get_db
from datetime import datetime, timezone, timedelta
from src.databases.models import User
from src.cache_func.user_cache import get_user_from_cache, set_user_to_cache

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє пароль користувача.
        :param plain_password: пароль користувача
        :param hashed_password: хеш пароль користувача
        :return: true or false
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Генерує хеш для паролю користувача.
        :param password: пароль користувача
        :return: Хеш паролю
        """
        return self.pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta=3600):
    """
    Створює JWT access token для автентифікації користувача.

    Args:
        data (dict): Дані, які будуть закодовані в токен (наприклад, {"sub": email}).
        expires_delta (int, optional): Час життя токена в секундах. За замовчуванням 3600 секунд (1 година).

    Returns:
        str: JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_password_reset_token(email: str, expires_delta=timedelta(hours=1)):
    to_encode = {"sub": email, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def verify_password_reset_token(token: str): 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None



async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db = Depends(get_db)
):
    """
    Отримує поточного авторизованого користувача з кешу Redis або бази даних на основі JWT токена.

    Спочатку функція перевіряє наявність даних користувача в Redis. Якщо кеш порожній або недійсний,
    тоді звертається до бази даних, отримує користувача та зберігає його в Redis для подальшого використання.

    Args:
        token (HTTPAuthorizationCredentials): JWT токен з заголовка Authorization.
        db (Session): Сесія бази даних, отримана через Depends(get_db).

    Raises:
        HTTPException: Якщо токен недійсний або користувача не знайдено.

    Returns:
        User: Об'єкт користувача.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user = await get_user_from_cache(email)
    if cached_user:
        return User(**cached_user)

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    await set_user_to_cache(user)
    return user