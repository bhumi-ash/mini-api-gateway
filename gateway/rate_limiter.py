import redis
import os
import time

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
)

RATE_LIMIT = 10          # max requests
WINDOW_SECONDS = 10      # per this many seconds

def is_allowed(user_id: str) -> bool:
    key = f"ratelimit:{user_id}"
    current = redis_client.incr(key)
    if current == 1:
        # first request in this window, set the expiry
        redis_client.expire(key, WINDOW_SECONDS)
    return current <= RATE_LIMIT

BUCKET_CAPACITY = 10
REFILL_RATE = 1  # tokens added per second

def is_allowed_token_bucket(user_id: str) -> bool:
    key = f"bucket:{user_id}"
    now = time.time()

    bucket = redis_client.hgetall(key)
    if not bucket:
        tokens = BUCKET_CAPACITY
        last_refill = now
    else:
        tokens = float(bucket["tokens"])
        last_refill = float(bucket["last_refill"])

    # refill tokens based on time passed
    elapsed = now - last_refill
    tokens = min(BUCKET_CAPACITY, tokens + elapsed * REFILL_RATE)

    if tokens < 1:
        redis_client.hset(key, mapping={"tokens": tokens, "last_refill": now})
        return False

    tokens -= 1
    redis_client.hset(key, mapping={"tokens": tokens, "last_refill": now})
    return True

