from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

# OAuth2PasswordBearer gets the token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Endpoint for login

# SECRET_KEY, ALGORITHM, and ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.secret_key  # This is taken from your settings (e.g., a .env file or config)
ALGORITHM = settings.algorithm  # For example, 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes  # How long tokens are valid

# Function to create a JWT token with username included
def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Expire time for the token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Function to verify and decode the access token
def verify_access_token(token: str, credentials_exception):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the user ID and username from the token
        id: str = payload.get("user_id")
        username: str = payload.get("username")  # Make sure you include 'username' in the payload

        # If the user ID is not found, raise an exception
        if id is None or username is None:
            raise credentials_exception
        
        # Return token data, including both the user ID and username
        token_data = schemas.TokenData(id=id, username=username)
    
    except JWTError:
        raise credentials_exception
    
    return token_data

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token and extract user info
    token_data = verify_access_token(token, credentials_exception)

    # Query the database for the user using the extracted user ID
    user = db.query(models.User).filter(models.User.id == token_data.id).first()

    # If user does not exist, raise an exception
    if user is None:
        raise credentials_exception

    # Return the user object (including username)
    return user
