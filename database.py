from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from model import Customer, Login, Book, Cart, Order
from hashing import Hash
from fastapi import HTTPException, Depends, Request, status
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


async def find_customer_by_id(cust_id: str):
    customer: Customer = await db.customers.find_one({"_id": ObjectId(cust_id)})
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error in fetching customer')
    return customer


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


async def fetch_cart_for_cust(cust_id: str):
    customer: Customer = await find_customer_by_id(cust_id)
    cart = customer['cart']
    cartItems = []
    for book_id in cart:
        cust_book = await find_book_by_id(book_id)
        cartItems.append({
            "_id": cust_book["_id"],
            "title": cust_book["title"],
            "author": cust_book["author"],
            "cover_image_url": cust_book["cover_image_url"],
        })

    return cartItems


async def cart(request: Cart, type: str):
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


async def fetch_order_for_cust(cust_id: str):
    customer: Customer = await find_customer_by_id(cust_id)
    orders = customer['orders']
    orderItems = []
    for order in orders:
        book_id = order["order_id"]
        order_date = order["order_date"]
        cust_book = await find_book_by_id(book_id)
        orderItems.append({
            "_id": cust_book["_id"],
            "title": cust_book["title"],
            "author": cust_book["author"],
            "cover_image_url": cust_book["cover_image_url"],
            "created": order_date
        })
    return orderItems


async def add_order(request: Order):

    cust_id = request.cust_id
    book_id = request.book_id
    order_date = request.order_date

    customer: Customer = await find_customer_by_id(cust_id)
    orders = customer['orders']
    orders.append({"order_id": book_id, "order_date": order_date})
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


async def search_books(search_query: str, genre: str, minPrice: int, maxPrice: int, minDate: int, maxDate: int):

    root_clause = {}
    db_query = []
    if search_query:

        db_query.append({
            "$or": [
                {"title": {"$regex": search_query, '$options': 'i'}},
                {"author": {"$regex": search_query, '$options': 'i'}},
                {"genre": {"$regex": search_query, '$options': 'i'}}
            ]
        })

    if genre:
        db_query.append({
            "genre": {"$regex": genre}
        })

    if minPrice:
        db_query.append({
            "price": {"$gte": minPrice}
        })

    if maxPrice:
        db_query.append({
            "price": {"$lte": maxPrice}
        })

    if minDate:
        db_query.append({
            "publication_date": {"$gte": minDate}
        })

    if maxDate:
        db_query.append({
            "publication_date": {"$lte": maxDate}
        })

    if db_query:
        root_clause = {"$and": db_query}

    print(root_clause)

    cursor = db.books.find(root_clause)
    if not cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Error fetching books')
    books = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        books.append(document)
    return books
