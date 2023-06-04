
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth_bearer import JWTBearer
from model import Customer, Login
from database import (
    create_customer,
    login
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
def read_root():
    return {"data": "Hello World"}


@app.post('/api/register')
async def add_customer(request: Customer):
    response = await create_customer(request)
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@app.post('/api/login')
async def sign_in(request: Login):
    response = await login(request)
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@app.get('/api/listBooks', dependencies=[Depends(JWTBearer())])
async def listBooks():
    return {"Hi": "Hello"}
