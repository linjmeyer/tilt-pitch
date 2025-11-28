import time
from typing import Optional


class RateLimitedException(Exception):
    pass


class DeviceRateLimiter:
    def __init__(self, rate=1, period=1):
        self.default_rate = rate
        self.default_period = period
        self.device_limiters = dict()

    def approve(self, device_id):
        if device_id not in self.device_limiters:
            # No limiter for this device yet
            self.device_limiters[device_id] = self._get_new_limiter()
        # Check if this color is too frequent
        limiter = self.device_limiters[device_id]
        limiter.approve()

    def _get_new_limiter(self):
        return RateLimiter(self.default_rate, self.default_period)


class RateLimiter:
    def __init__(self, rate=1, period=1):
        self.rate: int = rate
        self.period: int = period
        self.allowance: int = rate
        self.last_check: Optional[float] = None

    def approve(self):
        if self.last_check is None:
            # first time checking, approve
            self.last_check = time.time()
            return

        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance = self.allowance + time_passed * (self.rate / self.period)
        if self.allowance > self.rate:
            self.allowance = self.rate
        if self.allowance < 1:
            raise RateLimitedException()
        else:
            self.allowance = self.allowance - 1

