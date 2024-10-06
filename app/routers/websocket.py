from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from .. import oauth2, models, schemas
from ..database import get_db

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
        user_list = ",".join([f"#{client_id}" for client_id in self.active_connections.keys()])
        for connection in self.active_connections.values():
            await connection.send_text(f"online_users:{user_list}")

    async def send_personal_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str, exclude: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

manager = ConnectionManager()

async def get_current_user_from_ws(websocket: WebSocket, token: str):
    credentials_exception = HTTPException(status_code=403, detail="Invalid token or credentials")
    token_data = oauth2.verify_access_token(token, credentials_exception)
    return token_data.username, token_data.id  # Include user_id

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    client_username, client_id = await get_current_user_from_ws(websocket, token)
    await manager.connect(websocket, client_username)
    
    # Retrieve and send previous messages
    messages = db.query(models.Message, models.User.username).join(models.User).order_by(models.Message.timestamp).all()
    for message, username in messages:
        if username == client_username:
            await websocket.send_text(f"You: {message.content}")
        else:
            await websocket.send_text(f"{username}: {message.content}")

    await manager.broadcast(f"Client #{client_username} has joined the chat!", exclude=client_username)

    try:
        while True:
            data = await websocket.receive_text()
            
            # Broadcast message to others
            await manager.broadcast(f"Client #{client_username}: {data}", exclude=client_username)
            
            # Send personal message as "You" to the current client
            await manager.send_personal_message(websocket, f"You: {data}")
            
            # Save the message to the database
            new_message = models.Message(content=data, user_id=client_id)
            db.add(new_message)
            db.commit()

    except WebSocketDisconnect:
        manager.disconnect(client_username)
        await manager.broadcast(f"Client #{client_username} left the chat")
        await manager.send_online_users_list()
