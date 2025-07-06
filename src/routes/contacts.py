from fastapi import APIRouter, Depends, status, HTTPException, Query
from src.repository import crud
from src.schemas.contact import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    ContactBase,
    ContactDeleted,
)
from src.databases.connect import get_db
from src.auth.auth import get_current_user

router = APIRouter(
    prefix="/contacts", tags=["contacts"], dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    name="Create contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    contact: ContactCreate, db=Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Створює новий контакт для поточного користувача.

    - **contact**: дані контакту
    - **current_user**: користувач, який створює контакт
    - **db**: сесія бази даних

    Returns:
        Створений контакт.
    """
    contact = await crud.create_contact(contact, current_user, db)
    return contact


@router.get("/", name="Get contacts", status_code=status.HTTP_200_OK)
async def read_all(db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Отримує список усіх контактів поточного користувача.

    Returns:
        Список контактів.
    """
    contacts = await crud.get_contacts(current_user, db)
    return contacts


@router.get("/search", response_model=list[ContactBase])
async def search_contacts(
    first_name=Query(None),
    last_name=Query(None),
    email=Query(None),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Пошук контактів за ім'ям, прізвищем або email.

    Parameters:
        - first_name: ім’я (необов’язково)
        - last_name: прізвище (необов’язково)
        - email: email (необов’язково)

    Returns:
        Список знайдених контактів.
    """
    find_contact = await crud.find_search(first_name, last_name, email, current_user, db)
    if not find_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return find_contact


@router.get("/upcoming-birthdays", response_model=list[ContactBase])
async def get_upcoming_birthdays(
    db=Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Повертає список контактів з днем народження протягом наступного тижня.

    Returns:
        Список контактів з майбутніми днями народження.
    """
    contacts_by_birthday = await crud.contacts_birthday(current_user, db)
    if not contacts_by_birthday:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contacts_by_birthday


@router.get(
    "/{contact_id}",
    name="Get contact By ID",
    response_model=ContactBase,
    status_code=status.HTTP_200_OK,
)
async def read(contact_id, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Отримує контакт за його унікальним ідентифікатором.

    Parameters:
        - contact_id: ID контакту

    Returns:
        Об'єкт контакту.
    """
    contact = await crud.get_contact_by_ID(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put(
    "/{contact_id}",
    name="Update contact By ID",
    response_model=ContactBase,
    status_code=status.HTTP_200_OK,
)
async def update(
    contact: ContactUpdate,
    contact_id,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Оновлює контакт за вказаним ID.

    Parameters:
        - contact_id: ID контакту
        - contact: нові дані для оновлення

    Returns:
        Оновлений контакт.
    """
    updated = await crud.update_contact(contact, contact_id, current_user, db)
    if updated is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete(
    "/{contact_id}", name="Delete contact By ID", response_model=ContactDeleted
)
async def delete(
    contact_id, db=Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Видаляє контакт за ID.

    Parameters:
        - contact_id: ID контакту

    Returns:
        Видалений контакт.
    """
    deleted = await crud.delete_contact(contact_id, current_user, db)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted
