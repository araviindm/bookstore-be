from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from model import Customer, Login, Book, Item
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
    customer_object = dict(request)
    customer_object["password"] = hashed_pass
    customer = await db.customers.find_one({"email": customer_object["email"]})
    if not customer:
        cust_id = await db.customers.insert_one(customer_object)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{customer_object["email"]} already exists')
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
                            detail=f'Error fetching books')
    books = []
    async for document in cursor:
        books.append(Book(**document))
    return books


async def cart(request: Item, type: str):
    cust_id = request.cust_id
    book_id = request.book_id
    customer: Customer = await find_customer_by_id(cust_id)
    cart = customer['cart']
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
    db_resp = await db.customers.update_one({"_id": ObjectId(cust_id)}, {"$set": {"cart": cart}})
    if not db_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error adding to cart')
    return resp


async def add_order(request: Item):
    cust_id = request.cust_id
    book_id = request.book_id
    customer: Customer = await find_customer_by_id(cust_id)
    orders = customer['orders']
    orders.append(book_id)
    db_resp = await db.customers.update_one({"_id": ObjectId(cust_id)}, {"$set": {"orders": orders}})
    if not db_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error adding to cart')
    return {"res": "added"}


async def find_customer_by_id(cust_id: str):
    customer: Customer = await db.customers.find_one({"_id": ObjectId(cust_id)})
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error in fetching customer')
    return customer


async def search_books(query: str):
    cursor = db.books.find({
        "$or": [
            {"title": {"$regex": query, '$options': 'i'}},
            {"author": {"$regex": query, '$options': 'i'}},
            {"genre": {"$regex": query, '$options': 'i'}}
        ]
    })
    if not cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error fetching books')
    books = []
    async for document in cursor:
        books.append(Book(**document))
    return books
