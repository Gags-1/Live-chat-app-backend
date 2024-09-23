from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from .. import oauth2

router = APIRouter(tags=["Websockets"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.send_online_users_list()

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_online_users_list(self):
        user_list = ",".join([f"Client#{client_id}" for client_id    in self.active_connections.keys()])
        for connection in self.active_connections.values():
            await connection.send_text(f"online_users:{user_list}")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

async def get_current_user_from_ws(websocket: WebSocket, token: str):
    credentials_exception = HTTPException(status_code=403, detail="Invalid token or credentials")
    token_data = oauth2.verify_access_token(token, credentials_exception)
    return token_data.username

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    client_id = await get_current_user_from_ws(websocket, token)
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"Client #{client_id} has joined the chat!")

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")
        await manager.send_online_users_list()
