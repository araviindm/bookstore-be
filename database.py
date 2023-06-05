from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from model import Customer, Login, Book, Cart
from hashing import Hash
from fastapi import HTTPException, Depends, status
from auth_handler import signJWT
from decouple import config


MONGODB_URI = config('MONGODB_URI')
client = AsyncIOMotorClient(MONGODB_URI)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.BookStore


async def create_customer(request: Customer):
    hashed_pass = Hash.bcrypt(request.password)
    user_object = dict(request)
    user_object["password"] = hashed_pass
    user = await db.customers.find_one({"email": user_object["email"]})
    if not user:
        user_id = await db.customers.insert_one(user_object)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{user_object["email"]} already exists')
    return {"res": "created"}


async def login(request: Login):
    user = await db.customers.find_one({"email": request.email})
    if (not user) or (not Hash.verify(user["password"], request.password)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Wrong email or password')
    return signJWT(user["email"])


async def fetch_books():
    cursor = db.books.find({})
    if not cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error in fetching books')
    books = []
    async for document in cursor:
        books.append(Book(**document))
    return books


async def cart(request: Cart, type: str):
    user_id = request.cust_id
    book_id = request.book_id
    user: Customer = await db.customers.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error adding to cart')
    cart = user['cart']
    resp = {}
    if type == "add":
        cart.append(book_id)
        resp = {"res": "added"}
    else:
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Cart is empty')
        cart.remove(book_id)
        resp = {"res": "deleted"}

    db_resp = await db.customers.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": cart}})
    if not db_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error adding to cart')
    return resp
