from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import websocket, user, auth


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def check():
    return {"message": "HELLO HELLO"}

app.include_router(websocket.router)
app.include_router(user.router)
app.include_router(auth.router)
