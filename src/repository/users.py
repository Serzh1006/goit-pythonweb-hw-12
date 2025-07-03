from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from src.auth.auth import Hash
from src.databases.models import User
from src.auth.auth import get_current_user

hasher = Hash()


async def admin_required(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def create_user(user_data, db):
    """
    Створює нового користувача у базі даних.

    Args:
        user_data: Дані користувача, що включають ім'я, email і пароль.
        db: Сесія бази даних SQLAlchemy.

    Returns:
        User: Створений об'єкт користувача.
    """
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hasher.get_password_hash(user_data.password),
        avatar=None,
        role = user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def authenticate_user(email: str, password: str, db):
    """
    Перевіряє облікові дані користувача під час логіну.

    Args:
        email (str): Email користувача.
        password (str): Пароль у відкритому вигляді.
        db: Сесія бази даних SQLAlchemy.

    Returns:
        User | None: Користувач, якщо автентифікація пройшла успішно, або None.
    """
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user or not hasher.verify_password(password, user.password):
        return None
    return user
