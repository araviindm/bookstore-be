
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth_bearer import JWTBearer
from model import Customer, Login, Item
from database import (
    create_customer,
    login,
    fetch_books,
    cart,
    add_order
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


@private_routes.get('/getbooks')
async def get_books():
    response = await fetch_books()
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@private_routes.post('/cart')
async def post_cart(request: Item):
    response = await cart(request, "add")
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@private_routes.delete('/cart')
async def delete_cart(request: Item):
    response = await cart(request, "delete")
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@private_routes.post('/order')
async def post_order(request: Item):
    response = await add_order(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


app.include_router(public_routes)
app.include_router(private_routes)
