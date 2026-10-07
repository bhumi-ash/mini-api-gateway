import asyncio
import time
from rate_limiter import is_allowed


def test_rate_limiter():
    async def run_test():
        user_allow = f"test-user-allows-{time.time_ns()}"
        user_block = f"test-user-blocks-{time.time_ns()}"

        # Under the limit
        assert await is_allowed(user_allow) is True

        # First 10 requests are allowed
        for _ in range(10):
            assert await is_allowed(user_block) is True

        # 11th request is blocked
        assert await is_allowed(user_block) is False

    asyncio.run(run_test())