
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


class Customer(BaseModel):
    _id: ObjectId
    name: str
    email: EmailStr
    password: str
    orders: Optional[list[dict]]
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


class Cart(BaseModel):
    cust_id: str
    book_id: str

    @validator('cust_id')
    def validate_cust_id(cls, cust_id_value):
        if not ObjectId.is_valid(cust_id_value):
            raise ValueError('Invalid cust id')
        return cust_id_value

    @validator('book_id')
    def validate_book_id(cls, book_id_value):
        if not ObjectId.is_valid(book_id_value):
            raise ValueError('Invalid book id')
        return book_id_value


class Order(BaseModel):
    cust_id: str
    order_date: int
    book_id: str

    @validator('cust_id')
    def validate_cust_id(cls, cust_id_value):
        if not ObjectId.is_valid(cust_id_value):
            raise ValueError('Invalid cust id')
        return cust_id_value

    @validator('book_id')
    def validate_book_id(cls, book_id_value):
        if not ObjectId.is_valid(book_id_value):
            raise ValueError('Invalid book id')
        return book_id_value

    @validator('order_date')
    def validate_order_date(cls, order_date_value):
        if order_date_value < 0:
            raise ValueError('Invalid epoch timestamp')

        return order_date_value
