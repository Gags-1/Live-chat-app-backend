from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(
    tags=["Websockets"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}  # Store connections by client_id

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.send_online_users_list()  # Send updated user list to all clients

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_online_users_list(self):
        # Prepare a list of currently online users
        user_list = ",".join([f"Client#{client_id}" for client_id in self.active_connections.keys()])
        # Notify all clients of the current online users
        for connection in self.active_connections.values():
            await connection.send_text(f"online_users:{user_list}")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"Client #{client_id} has joined the chat!")

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")
        await manager.send_online_users_list()  # Update user list after disconnect
