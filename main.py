
import os
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth_bearer import JWTBearer
from model import Customer, Login
from database import (
    create_customer,
    login,
    fetch_books
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


@app.post('/api/register')
async def register(request: Customer):
    response = await create_customer(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@app.post('/api/login')
async def signin(request: Login):
    response = await login(request)
    if response:
        return response
    raise HTTPException(404, "Something went wrong")


@app.get('/api/getbooks', dependencies=[Depends(JWTBearer())])
async def get_books():
    response = await fetch_books()
    if response:
        return response
    raise HTTPException(404, "Something went wrong")
