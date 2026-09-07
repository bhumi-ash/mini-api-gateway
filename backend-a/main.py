from fastapi import FastAPI

app = FastAPI()

orders_db = [
    {"id": 1, "item": "Laptop", "status": "shipped"},
    {"id": 2, "item": "Mouse", "status": "pending"},
]

@app.get("/orders")
def get_orders():
    return {"orders": orders_db}

@app.post("/orders")
def create_order(item: str):
    new_order = {"id": len(orders_db) + 1, "item": item, "status": "pending"}
    orders_db.append(new_order)
    return new_order

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend-a"}
