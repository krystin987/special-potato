from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib

router = APIRouter()

# In-memory user store (for simplicity, replace with a database later)
users = {}

class User(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    users[user.username] = hashed_password
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: User):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if users.get(user.username) != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}