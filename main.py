
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from auth_bearer import JWTBearer
from model import Cart, Customer, Login, Book, Order
from database import (
    create_customer,
    login,
    fetch_books,
    find_book_by_id,
    cart,
    add_order,
    search_books,
    fetch_cart_for_cust,
    fetch_order_for_cust
)


app = FastAPI()

origins = ['http:localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get("/")
def root():
    return {"data": "Hello World"}


@app.get('/favicon.ico', deprecated=True)
async def favicon():
    return 1

public_routes = APIRouter(
    prefix="/api",
)

private_routes = APIRouter(
    prefix="/api",
    dependencies=[Depends(JWTBearer())]
)


@public_routes.post('/register')
async def register(request: Customer):
    response = await create_customer(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.post('/login')
async def signin(request: Login):
    response = await login(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.get('/book')
async def get_books():
    response = await fetch_books()
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.get('/book/{id}')
async def get_book(id: str):
    response: Book = await find_book_by_id(id)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.get('/cart/{cust_id}')
async def get_cart_for_cust(cust_id: str):
    response = await fetch_cart_for_cust(cust_id)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.post('/cart')
async def post_cart(request: Cart):
    response = await cart(request, "add")
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.delete('/cart')
async def delete_cart(request: Cart):
    response = await cart(request, "delete")
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.get('/order/{cust_id}')
async def get_order_for_cust(cust_id: str):
    response = await fetch_order_for_cust(cust_id)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.post('/order')
async def post_order(request: Order):
    response = await add_order(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@public_routes.get('/search')
async def search(search_query: str | None = None,
                 genre: str | None = None,
                 minPrice: int | None = None,
                 maxPrice: int | None = None,
                 minDate: int | None = None,
                 maxDate: int | None = None):
    response = await search_books(search_query, genre, minPrice, maxPrice, minDate, maxDate)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")

app.include_router(public_routes)
app.include_router(private_routes)
