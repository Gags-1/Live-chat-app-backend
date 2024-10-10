from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    username: str

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    user_id: int
    username: str  # We now include the username for clarity
    timestamp: datetime

    class Config:
        from_attributes = True

# Schemas for managing friendships
class FriendRequest(BaseModel):
    friend_id: int

class FriendResponse(BaseModel):
    id: int
    username: str
    status: str  # Status of friendship (pending, accepted, declined)
