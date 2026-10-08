from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "change-this-to-something-random-later"
ALGORITHM = "HS256"

FAKE_USERS = {
    f"user{i}": {"password": "pass123", "user_id": str(i)}
    for i in range(1, 201)
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