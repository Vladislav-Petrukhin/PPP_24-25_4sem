from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active[user_id].add(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        self.active[user_id].discard(ws)

    async def broadcast(self, user_id: int, message: dict):
        for ws in list(self.active[user_id]):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, ws)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = int(payload["sub"])

    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # PING/PONG от клиента
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
