from motor.motor_asyncio import AsyncIOMotorClient
from model import Customer
from hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm
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

database = client.BookStore
collection = database.customers


async def create_customer(request: Customer):
    hashed_pass = Hash.bcrypt(request.password)
    user_object = dict(request)
    user_object["password"] = hashed_pass
    user = await collection.find_one({"email": user_object["email"]})
    if not user:
        user_id = await collection.insert_one(user_object)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{user_object["email"]} already exists')

    print(user_id)
    return {"res": "created"}


async def login(request: OAuth2PasswordRequestForm = Depends()):
    user = await collection.find_one({"email": request.email})
    if (not user) or (not Hash.verify(user["password"], request.password)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Wrong email or password')
    return signJWT(user["email"])
