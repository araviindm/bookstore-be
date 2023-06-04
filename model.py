from pydantic import BaseModel
from typing import Optional
from uuid import uuid4


class Books(BaseModel):
    id: uuid4
    title: str
    author: str
    description: str
    cover_image: str
    price: int
    genre: str
    publication_date: int
    customer_ratings: str


class Customer(BaseModel):
    id: uuid4
    email: str
    password: str
    orders: set
    cart: set


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
