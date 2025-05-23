from fastapi import FastAPI
from app.api import users, parse  # Убедись, что users.py и parse.py экспортируют router

app = FastAPI()

app.include_router(users.router)
app.include_router(parse.router)
