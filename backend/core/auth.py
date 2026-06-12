"""
Authentication utilities — JWT tokens, PIN hashing, role checks.
"""
import os
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "tumaini-secret-change-in-production")
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)

def hash_pin(pin: str) -> str:
    """SHA-256 hash a PIN — never store PINs in plaintext."""
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin: str, pin_hash: str) -> bool:
    return hash_pin(pin) == pin_hash

def generate_pin(length: int = 4) -> str:
    """Generate a random numeric PIN."""
    return "".join(secrets.choice(string.digits) for _ in range(length))

def generate_user_id(role: str) -> str:
    prefix = {"admin": "ADM", "chw": "CHW", "patient": "PAT"}.get(role, "USR")
    suffix = secrets.token_hex(4).upper()
    return f"{prefix}-{suffix}"

def create_token(user_id: str, role: str, phone: str) -> str:
    payload = {
        "sub":   user_id,
        "role":  role,
        "phone": phone,
        "exp":   datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return decode_token(credentials.credentials)

def require_role(*roles):
    """Dependency factory — restrict endpoint to specific roles."""
    def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {', '.join(roles)}"
            )
        return user
    return checker

# Convenience dependencies
require_admin   = require_role("admin")
require_chw     = require_role("admin", "chw")
require_patient = require_role("admin", "chw", "patient")
