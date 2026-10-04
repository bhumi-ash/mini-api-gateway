from circuit_breaker import breakers
from rate_limiter import is_allowed
from prometheus_fastapi_instrumentator import Instrumentator

from fastapi import FastAPI, Request, Response, HTTPException
import httpx

from auth import create_token, verify_token, FAKE_USERS


app = FastAPI()

Instrumentator().instrument(app).expose(app)


# Which backend handles which path prefix
ROUTES = {
    "orders": "http://backend-a:8000",
    "users": "http://backend-b:8000",
}


@app.post("/login")
def login(username: str, password: str):
    user = FAKE_USERS.get(username)

    if not user or user["password"] != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token(user["user_id"])

    return {"access_token": token}


@app.api_route(
    "/api/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def gateway_forward(
    service: str,
    path: str,
    request: Request
):
    authorization = request.headers.get("authorization")

    # Check Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    # Extract token
    token = authorization.split(" ")[1]

    # Verify JWT
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Rate limiting
    if not is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded, slow down"
        )

    # Check whether the requested service exists
    if service not in ROUTES:
        return Response(
            content="Unknown service",
            status_code=404
        )

    # Build the backend URL
    target_url = f"{ROUTES[service]}/{service}"

    if path:
        target_url += f"/{path}"

    # Read request body
    body = await request.body()

    # Get the circuit breaker for this service
    breaker = breakers.get(service)

    # Check whether the circuit is open
    if breaker and not breaker.allow_request():
        raise HTTPException(
            status_code=503,
            detail=f"{service} service temporarily unavailable (circuit open)"
        )

    # Forward request to backend
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            backend_response = await client.request(
                method=request.method,
                url=target_url,
                headers={
                    **{
                        k: v
                        for k, v in request.headers.items()
                        if k.lower() != "host"
                    },
                    "X-User-Id": user_id,
                },
                content=body,
                params=request.query_params,
            )

        # Backend request succeeded
        if breaker:
            breaker.record_success()

    except httpx.RequestError:
        # Backend request failed
        if breaker:
            breaker.record_failure()

        raise HTTPException(
            status_code=503,
            detail=f"{service} service is down"
        )

    # Return backend response to client
    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers),
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "gateway"
    }