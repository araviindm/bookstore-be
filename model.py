
from typing import Optional
from bson import ObjectId

from pydantic import BaseModel, EmailStr, validator


class Book(BaseModel):
    _id: ObjectId
    title: str
    author: str
    description: Optional[str]
    cover_image_url: Optional[str]
    price: int
    genre: str
    publication_date: int
    customer_ratings: str

    @validator('publication_date')
    def validate_publication_date(cls, publication_date_value):

        if publication_date_value < 0:
            raise ValueError('Invalid epoch timestamp')

        return publication_date_value


class Item(BaseModel):
    _id: ObjectId
    book_id: str
    cust_id: str
    order_date: int

    @validator('book_id', 'cust_id')
    def validate_fields(cls, id_values):

        book_id, cust_id, order_date = id_values
        if not ObjectId.is_valid(book_id):
            raise ValueError('Invalid book id')

        if not ObjectId.is_valid(cust_id):
            raise ValueError('Invalid customerid')

        if order_date < 0:
            raise ValueError('Invalid epoch timestamp')

        return id_values


class Order():
    Item


class Cart():
    Item


class Customer(BaseModel):
    _id: ObjectId
    name: str
    email: EmailStr
    password: str
    orders: Optional[list[str]]
    cart: Optional[list[str]]

    @validator('name')
    def validate_fields(cls, name_value):

        if not name_value.strip():
            raise ValueError('Name cannot be empty')

        return name_value

    class Config:
        validate_assignment = True

    @validator('password')
    def validate_password(cls, password_value):
        if not password_value.strip():
            raise ValueError('Password cannot be empty')

        min_password_length = 6
        if len(password_value) < min_password_length:
            raise ValueError(
                f'Password must be at least {min_password_length} characters long')

        if not any(char.isupper() for char in password_value):
            raise ValueError(
                'Password must contain at least one uppercase letter')

        if not any(char.islower() for char in password_value):
            raise ValueError(
                'Password must contain at least one lowercase letter')

        if not any(char.isdigit() for char in password_value):
            raise ValueError('Password must contain at least one digit')

        return password_value


class Login(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, password_value):
        if not password_value.strip():
            raise ValueError('Password cannot be empty')

        min_password_length = 6
        if len(password_value) < min_password_length:
            raise ValueError(
                f'Password must be at least {min_password_length} characters long')

        if not any(char.isupper() for char in password_value):
            raise ValueError(
                'Password must contain at least one uppercase letter')

        if not any(char.islower() for char in password_value):
            raise ValueError(
                'Password must contain at least one lowercase letter')

        if not any(char.isdigit() for char in password_value):
            raise ValueError('Password must contain at least one digit')

        return password_value

    class Config:
        validate_assignment = True
