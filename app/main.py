from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .routers import websocket
from .database import engine, Base
from .models import User  # Import your models

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Import routers
from .routers import users, websocket

app = FastAPI()

# Enable CORS so the frontend (which will be served from a different server or port) can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to your frontend server)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def check():
    return {"message": "HELLO HELLO"}

# Include routers
app.include_router(websocket.router)
app.include_router(users.router)
