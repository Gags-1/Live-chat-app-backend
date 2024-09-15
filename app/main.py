from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import websocket


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

app.include_router(websocket.router)
