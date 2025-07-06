from src.databases.models import Contact, User
from datetime import datetime, timedelta
from sqlalchemy import select, and_


async def create_contact(contact, current_user: User, db):
    """
    Створює новий контакт для поточного користувача.

    Args:
        contact: Схема даних нового контакту.
        current_user (User): Поточний авторизований користувач.
        db: Сесія бази даних.

    Returns:
        Contact: Створений контакт.
    """
    new_contact = Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def get_contacts(current_user: User, db):
    """
    Отримує всі контакти поточного користувача.

    Args:
        current_user (User): Поточний авторизований користувач.
        db: Сесія бази даних.

    Returns:
        List[Contact]: Список контактів.
    """
    stmt = select(Contact).where(Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_contact_by_ID(contact_id: int, current_user: User, db):
    """
    Повертає контакт за його ідентифікатором для поточного користувача.

    Args:
        contact_id (int): Ідентифікатор контакту.
        current_user (User): Поточний авторизований користувач.
        db: Сесія бази даних.

    Returns:
        Contact | None: Контакт або None, якщо не знайдено.
    """
    stmt = select(Contact).where(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    )
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact


async def update_contact(contact_data, contact_id: int, current_user: User, db):
    """
    Оновлює дані контакту поточного користувача.

    Args:
        contact_data: Нові дані для оновлення.
        contact_id (int): Ідентифікатор контакту.
        current_user (User): Поточний користувач.
        db: Сесія бази даних.

    Returns:
        Contact | None: Оновлений контакт або None, якщо не знайдено.
    """
    contact = await get_contact_by_ID(contact_id, current_user, db)
    if contact:
        for key, value in contact_data.dict().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, current_user: User, db):
    """
    Видаляє контакт поточного користувача за ID.

    Args:
        contact_id (int): Ідентифікатор контакту.
        current_user (User): Поточний користувач.
        db: Сесія бази даних.

    Returns:
        Contact | None: Видалений контакт або None, якщо не знайдено.
    """
    contact = await get_contact_by_ID(contact_id, current_user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_search(first_name, last_name, email, current_user: User, db):
    """
    Шукає контакти поточного користувача за іменем, прізвищем або email.

    Args:
        first_name (str | None): Ім’я для пошуку.
        last_name (str | None): Прізвище для пошуку.
        email (str | None): Email для пошуку.
        current_user (User): Поточний користувач.
        db: Сесія бази даних.

    Returns:
        List[Contact]: Список знайдених контактів.
    """
    filters = [Contact.user_id == current_user.id]

    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    stmt = select(Contact).where(and_(*filters))
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def contacts_birthday(current_user: User, db):
    """
    Повертає контакти, у яких день народження протягом наступних 7 днів.

    Args:
        current_user (User): Поточний користувач.
        db: Сесія бази даних.

    Returns:
        List[Contact]: Список контактів з майбутніми днями народження.
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    stmt = select(Contact).where(Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    upcoming = []

    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                upcoming.append(contact)

    return upcoming
