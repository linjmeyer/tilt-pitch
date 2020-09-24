import time


class RateLimitedException(Exception):
    pass


class RateLimiter:
    def __init__(self, rate=1, period=1):
        self.rate = rate
        self.period = period
        self.allowance = rate
        self.last_check = time.time()

    def approve(self):
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
