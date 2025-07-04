import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, timedelta
from src.repository.crud import update_contact, delete_contact, create_contact, contacts_birthday, get_contact_by_ID, get_contacts, find_search
from src.databases.models import Contact, User

@pytest.fixture
def current_user():
    user = User()
    user.id = 1
    return user

@pytest.fixture
def db():
    session = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session


@pytest.mark.asyncio
async def test_create_contact(db, current_user):
    contact_data = MagicMock()
    contact_data.model_dump.return_value = {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'}

    result = await create_contact(contact_data, current_user, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None
    assert isinstance(result, Contact)

@pytest.mark.asyncio
async def test_get_contacts(db, current_user):
    fake_contacts = [Contact(), Contact()]
    query_mock = MagicMock()
    query_mock.filter.return_value.all.return_value = fake_contacts
    db.query.return_value = query_mock

    result = await get_contacts(current_user, db)

    db.query.assert_called_once()
    assert result == fake_contacts

@pytest.mark.asyncio
async def test_get_contact_by_ID_found(db, current_user):
    fake_contact = Contact()
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = fake_contact
    db.query.return_value = query_mock

    result = await get_contact_by_ID(1, current_user, db)

    db.query.assert_called_once()
    assert result == fake_contact

@pytest.mark.asyncio
async def test_get_contact_by_ID_not_found(db, current_user):
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = None
    db.query.return_value = query_mock

    result = await get_contact_by_ID(999, current_user, db)

    assert result is None

@pytest.mark.asyncio
@patch('src.repository.crud.get_contact_by_ID')
async def test_update_contact_found(mock_get_contact, db, current_user):
    contact = Contact()
    contact.first_name = 'OldName'
    mock_get_contact.return_value = contact

    contact_data = MagicMock()
    contact_data.dict.return_value = {'first_name': 'Jane'}

    result = await update_contact(contact_data, 1, current_user, db)

    mock_get_contact.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(contact)
    assert result.first_name == 'Jane'

@pytest.mark.asyncio
@patch('src.repository.crud.get_contact_by_ID')
async def test_update_contact_not_found(mock_get_contact, db, current_user):
    mock_get_contact.return_value = None

    contact_data = MagicMock()
    contact_data.dict.return_value = {'first_name': 'Jane'}

    result = await update_contact(contact_data, 1, current_user, db)

    mock_get_contact.assert_called_once()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    assert result is None

@pytest.mark.asyncio
@patch('src.repository.crud.get_contact_by_ID')
async def test_delete_contact_found(mock_get_contact, db, current_user):
    contact = Contact()
    mock_get_contact.return_value = contact

    result = await delete_contact(1, current_user, db)

    mock_get_contact.assert_called_once()
    db.delete.assert_called_once_with(contact)
    db.commit.assert_called_once()
    assert result == contact

@pytest.mark.asyncio
@patch('src.repository.crud.get_contact_by_ID')
async def test_delete_contact_not_found(mock_get_contact, db, current_user):
    mock_get_contact.return_value = None

    result = await delete_contact(1, current_user, db)

    mock_get_contact.assert_called_once()
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    assert result is None


def test_find_search(db, current_user):
    fake_contacts = [Contact(), Contact()]
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = fake_contacts
    db.query.return_value = query_mock

    result = find_search("John", None, None, current_user, db)

    db.query.assert_called_once()
    query_mock.filter.assert_called()  # Проверяем, что фильтрация применена
    assert result == fake_contacts

def test_contacts_birthday(db, current_user):
    today = date.today()
    contact1 = Contact()
    contact1.user_id = current_user.id
    contact1.birthday = today + timedelta(days=3)
    contact2 = Contact()
    contact2.user_id = current_user.id
    contact2.birthday = today + timedelta(days=10)  # вне диапазона
    contact3 = Contact()
    contact3.user_id = current_user.id
    contact3.birthday = None

    db.query.return_value.filter.return_value.all.return_value = [contact1, contact2, contact3]

    result = asyncio.run(contacts_birthday(current_user, db))

    assert contact1 in result
    assert contact2 not in result
    assert contact3 not in result