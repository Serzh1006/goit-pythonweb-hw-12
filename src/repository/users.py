from src.auth.auth import Hash
from src.databases.models import User

hasher = Hash()


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
    user = db.query(User).filter(User.email == email).first()
    if not user or not hasher.verify_password(password, user.password):
        return None
    return user
