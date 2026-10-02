import time

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=15):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"       # closed -> open -> half-open -> closed
        self.opened_at = None

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time.time()

    def allow_request(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = "half-open"
                return True   # allow ONE test request through
            return False
        if self.state == "half-open":
            return True
        return True

# one breaker per backend service
breakers = {
    "orders": CircuitBreaker(),
    "users": CircuitBreaker(),
}
