"""Token bucket 限流降级存根（D2）。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """简单 token bucket：容量 capacity，每秒 refill_rate 个令牌。"""

    capacity: float = 10.0
    refill_rate: float = 5.0  # tokens per second
    tokens: float = field(init=False)
    _last_refill: float = field(init=False)

    def __post_init__(self) -> None:
        self.tokens = self.capacity
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self._last_refill = now

    def allow(self, cost: float = 1.0) -> bool:
        """若有足够令牌则扣减并返回 True，否则拒绝（降级信号）。"""
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def degrade_hint(self) -> str:
        """限流时的降级提示。"""
        return "rate_limited: fall back to cheaper model or delay"
