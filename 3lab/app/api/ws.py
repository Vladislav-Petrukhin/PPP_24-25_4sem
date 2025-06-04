import logging
from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token

router = APIRouter()

# Используем логгер uvicorn.error — он принимает произвольные сообщения
logger = logging.getLogger("uvicorn.error")


class ConnectionManager:
    def __init__(self):
        self.active: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active[user_id].add(ws)
        # Записываем лог простыми сообщениями, без “распаковки” полей
        logger.info(f"WebSocket: user_id={user_id} connected (total sockets={len(self.active[user_id])})")

    def disconnect(self, user_id: int, ws: WebSocket):
        self.active[user_id].discard(ws)
        logger.info(f"WebSocket: user_id={user_id} disconnected (remaining sockets={len(self.active[user_id])})")

    async def broadcast(self, user_id: int, message: dict):
        logger.info(f"WebSocket broadcast to user_id={user_id}: {message!r}")
        to_remove = []
        for ws in list(self.active[user_id]):
            try:
                await ws.send_json(message)
            except Exception as e:
                to_remove.append(ws)
                logger.warning(f"WebSocket send error for user_id={user_id}: {e}")
        for ws in to_remove:
            self.disconnect(user_id, ws)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        logger.warning("WebSocket: invalid or missing token; closing connection")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = int(payload["sub"])
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"WebSocket received from user_id={user_id}: {data!r}")
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
