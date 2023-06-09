from bson.objectid import ObjectId
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
    customer = dict(request)
    resp = await db.customers.find_one({"email": customer["email"]})
    if not resp:
        hashed_pass = Hash.bcrypt(customer["password"])
        customer["password"] = hashed_pass
        cust_id = await db.customers.insert_one(customer)
        if not cust_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'Customer not created')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{customer["email"]} already exists')
    response = signJWT(customer["email"])
    response["email"] = customer["email"]
    response["name"] = customer["name"]
    return response


async def login(request: Login):
    customer: Customer = await db.customers.find_one({"email": request.email})
    if (not customer) or (not Hash.verify(customer["password"], request.password)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Wrong email or password')
    response = signJWT(customer["email"])
    response["email"] = customer["email"]
    response["name"] = customer["name"]
    return response


async def fetch_books():
    cursor = db.books.find({})
    if not cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error fetching books')
    books = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        books.append(document)
    return books


async def find_book_by_id(book_id: str):
    book: Book = await db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error in fetching book')
    book["_id"] = str(book["_id"])
    return book


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
        document["_id"] = str(document["_id"])
        books.append(document)
    return books

# async def cart(request: Item, type: str):
#     cust_id = request.cust_id
#     book_id = request.book_id
#     customer: Customer = await find_customer_by_id(cust_id)
#     cart = customer['cart']
#     resp = {}
#     if type == "add":
#         cart.append(book_id)
#         resp = {"res": "added"}
#     else:
#         if not cart:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                 detail=f'Cart is empty')
#         cart.remove(book_id)
#         resp = {"res": "deleted"}
#     db_resp = await db.customers.update_one({"_id": ObjectId(cust_id)}, {"$set": {"cart": cart}})
#     if not db_resp:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Error adding to cart')
#     return resp


# async def add_order(request: Item):
#     cust_id = request.cust_id
#     book_id = request.book_id
#     customer: Customer = await find_customer_by_id(cust_id)
#     orders = customer['orders']
#     orders.append(book_id)
#     db_resp = await db.customers.update_one({"_id": ObjectId(cust_id)}, {"$set": {"orders": orders}})
#     if not db_resp:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Error adding to cart')
#     return {"res": "added"}


# async def find_customer_by_id(cust_id: str):
#     customer: Customer = await db.customers.find_one({"_id": ObjectId(cust_id)})
#     if not customer:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Error in fetching customer')
#     return customer
