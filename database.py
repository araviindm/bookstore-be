from motor.motor_asyncio import AsyncIOMotorClient
from model import Customer, Login, Book
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
