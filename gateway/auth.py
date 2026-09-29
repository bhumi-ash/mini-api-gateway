from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "change-this-to-something-random-later"
ALGORITHM = "HS256"

FAKE_USERS = {
    "asha": {"password": "pass123", "user_id": "1"},
    "ravi": {"password": "pass456", "user_id": "2"},
}

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=2)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None