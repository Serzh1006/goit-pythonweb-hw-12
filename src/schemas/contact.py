from pydantic import BaseModel, EmailStr
from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class ContactDeleted(BaseModel):
    id: int
