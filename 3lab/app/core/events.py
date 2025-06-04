""" Диспетчер: раз в 0.2 c принимает новые события из таблицы events
и раздаёт активным WebSocket-клиентам (ConnectionManager). """
import asyncio, json, datetime
from sqlalchemy import select, update
from .database import SessionLocal
from app.models.event import Event
from app.api.ws import manager

POLL_INTERVAL = 0.2

async def _dispatch_loop():
    while True:
        async with asyncio.Lock():  # на всякий случай
            db = SessionLocal()
            events = db.execute(select(Event).where(Event.sent == False)).scalars().all()
            for ev in events:
                await manager.broadcast(ev.user_id, json.loads(ev.data))
                db.execute(update(Event).where(Event.id == ev.id).values(sent=True))
            db.commit()
            db.close()
        await asyncio.sleep(POLL_INTERVAL)

def start_event_dispatcher(app):
    loop = asyncio.get_event_loop()
    task = loop.create_task(_dispatch_loop())
    return task

async def stop_event_dispatcher(task):
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
