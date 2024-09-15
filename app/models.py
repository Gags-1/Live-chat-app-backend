from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey,Integer, String, Boolean, func, text, DateTime
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Add this line