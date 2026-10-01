"""Auth: bcrypt passwords + JWT tokens. Beginner: hash = one-way scramble,
token = stamped ID card the frontend shows on every request."""
import os
from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET = os.getenv("JWT_SECRET", "campus-mart-dev-secret-change-me")
ALGO = "HS256"
HOURS = 24
security = HTTPBearer(auto_error=False)


def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def check_pw(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def make_token(user_id: int) -> str:
    payload = {"uid": user_id, "exp": datetime.utcnow() + timedelta(hours=HOURS)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def need_user(creds: HTTPAuthorizationCredentials = Depends(security),
              db: Session = Depends(get_db)):
    if not creds:
        raise HTTPException(status_code=401, detail="Login required (missing token)")
    try:
        data = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
    except Exception:
        raise HTTPException(status_code=401, detail="Bad or expired token")
    user = db.get(models.User, data["uid"])
    if not user:
        raise HTTPException(status_code=401, detail="User gone")
    return user
