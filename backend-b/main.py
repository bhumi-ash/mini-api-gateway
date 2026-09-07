from fastapi import FastAPI

app = FastAPI()

users_db = {
    "1": {"id": "1", "name": "Asha"},
    "2": {"id": "2", "name": "Ravi"},
}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    return users_db.get(user_id, {"error": "not found"})

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend-b"}
