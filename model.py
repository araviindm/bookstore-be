from pydantic import BaseModel
from typing import Optional


class Books(BaseModel):
    title: str
    author: str
    description: str
    cover_image: str
    price: int
    genre: str
    publication_date: int
    customer_ratings: str


class Customer(BaseModel):
    email: str
    password: str
    orders: list[str]
    cart: list[str]


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
