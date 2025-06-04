from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, users, parse, ws
from .core.database import Base, engine
from .core.events import start_event_dispatcher, stop_event_dispatcher

# Создаём таблицы (быстрая инициалиzация; для продакшена используйте Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Site Parser & Graph Builder")

# CORS (при необходимости фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(parse.router, prefix="/api")
app.include_router(ws.router)

# Фоновая корутина, доставляющая WS-события из SQLite
@app.on_event("startup")
async def startup():
    app.state.dispatcher_task = start_event_dispatcher(app)

@app.on_event("shutdown")
async def shutdown():
    await stop_event_dispatcher(app.state.dispatcher_task)
