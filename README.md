## Book store

- There's a route to create 10 sample entries of books.
- I implemented the routes I thought were sufficient for the application.

## The .env file

JWT_SECRET= 
JWT_ALGORITHM= 
MONGODB_URI = 

## To install dependencies

python -m venv venv  
.\venv\Scripts\activate  
pip install -r requirements.txt

## To run

uvicorn main:app --reload
