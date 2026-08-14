"""基于 token 估算费用（D2）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostEstimate:
    """单次调用费用估算。"""

    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float


# Teaching stub prices ($ / 1K tokens).
_PRICE_PER_1K: dict[str, tuple[float, float]] = {
    "mock-small": (0.0001, 0.0002),
    "mock-large": (0.001, 0.002),
}


class CostMonitor:
    """累计 token 费用。"""

    def __init__(self) -> None:
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.calls: list[CostEstimate] = []

    def record(
        self,
        *,
        input_tokens: int,
        output_tokens: int,
        model: str = "mock-small",
    ) -> CostEstimate:
        """记录一次调用并返回费用明细。"""
        in_price, out_price = _PRICE_PER_1K.get(model, (0.001, 0.002))
        cost = (input_tokens / 1000.0) * in_price + (output_tokens / 1000.0) * out_price
        est = CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost_usd=round(cost, 8),
        )
        self.calls.append(est)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd = round(self.total_cost_usd + est.cost_usd, 8)
        return est

    def summary(self) -> dict:
        """汇总费用指标。"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "calls": len(self.calls),
        }
