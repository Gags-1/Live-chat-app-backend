from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/friends",
    tags=["Friends"]
)

# Send Friend Request
@router.post("/add", status_code=status.HTTP_201_CREATED)
def send_friend_request(request: schemas.FriendRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if the user exists
    friend = db.query(models.User).filter(models.User.id == request.friend_id).first()
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if the friendship already exists
    friendship = db.query(models.Friendship).filter(
        models.Friendship.user_id == current_user.id, 
        models.Friendship.friend_id == request.friend_id
    ).first()
    
    if friendship:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent")
    
    # Create a new friend request
    new_friendship = models.Friendship(user_id=current_user.id, friend_id=request.friend_id, status="pending")
    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)
    return {"message": "Friend request sent"}

# Accept Friend Request
@router.put("/accept/{friend_id}", status_code=status.HTTP_200_OK)
def accept_friend_request(friend_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    friendship = db.query(models.Friendship).filter(
        models.Friendship.user_id == friend_id, 
        models.Friendship.friend_id == current_user.id, 
        models.Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    
    friendship.status = "accepted"
    db.commit()
    return {"message": "Friend request accepted"}

# Decline Friend Request
@router.put("/decline/{friend_id}", status_code=status.HTTP_200_OK)
def decline_friend_request(friend_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    friendship = db.query(models.Friendship).filter(
        models.Friendship.user_id == friend_id, 
        models.Friendship.friend_id == current_user.id, 
        models.Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    
    friendship.status = "declined"
    db.commit()
    return {"message": "Friend request declined"}

# View Friends List
@router.get("/", response_model=List[schemas.FriendResponse])
def get_friends_list(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    friends = db.query(models.Friendship).filter(
        (models.Friendship.user_id == current_user.id) | (models.Friendship.friend_id == current_user.id),
        models.Friendship.status == "accepted"
    ).all()
        
    friends_list = []
    for friendship in friends:
        friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
        friend = db.query(models.User).filter(models.User.id == friend_id).first()
        friends_list.append({
            "id": friend.id,
            "username": friend.username,
            "status": friendship.status
        })
    
    return friends_list
