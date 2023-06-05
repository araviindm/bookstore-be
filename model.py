
from typing import Optional

from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    description: Optional[str]
    cover_image_url: Optional[str]
    price: int
    genre: list
    publication_date: int
    customer_ratings: str


class Customer(BaseModel):
    email: str
    password: str
    orders: Optional[list]
    cart: Optional[list]


class Login(BaseModel):
    email: str
    password: str


class Cart(BaseModel):
    cust_id: str
    book_id: str
