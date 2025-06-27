from src.databases.models import Contact, User
from datetime import datetime, timedelta


async def create_contact(contact, current_user: User, db):
    new_contact = Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


async def get_contacts(current_user: User, db):
    return db.query(Contact).filter(Contact.user_id == current_user.id).all()


async def get_contact_by_ID(contact_id: int, current_user: User, db):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()


async def update_contact(contact_data, contact_id: int, current_user: User, db):
    contact = await get_contact_by_ID(contact_id, current_user, db)
    if contact:
        for key, value in contact_data.dict().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, current_user: User, db):
    contact = await get_contact_by_ID(contact_id, current_user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def find_search(first_name, last_name, email, current_user: User, db):
    query = db.query(Contact).filter(Contact.user_id == current_user.id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


async def contacts_birthday(current_user: User, db):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    upcoming = []

    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                upcoming.append(contact)

    return upcoming