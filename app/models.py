from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, text

class User(Base):
    __tablename__="users"

    id=Column(Integer,primary_key=True, nullable=False)
    username=Column(String,nullable=False)
    email=Column(String, nullable=False, unique=True, index=True)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))
