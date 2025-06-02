from fastapi import FastAPI
from app.api.endpoints import users, tasks, admin
from app.db.session import engine, Base

app = FastAPI(title="LabParser Project")

app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
