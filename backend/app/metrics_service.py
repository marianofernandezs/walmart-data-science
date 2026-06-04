from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any


@dataclass
class MetricsService:
    response_times_ms: list[float] = field(default_factory=list)
    total_predictions: int = 0

    def record_response_time(self, elapsed_ms: float) -> None:
        self.response_times_ms.append(round(elapsed_ms, 2))
        if len(self.response_times_ms) > 500:
            self.response_times_ms = self.response_times_ms[-500:]

    def record_prediction(self, count: int = 1) -> None:
        self.total_predictions += count

    def snapshot(self, model_status: str, model_metrics: dict[str, Any]) -> dict[str, Any]:
        return {
            "average_response_time_ms": round(mean(self.response_times_ms), 2)
            if self.response_times_ms
            else 0.0,
            "total_predictions": self.total_predictions,
            "api_status": "online",
            "model_status": model_status,
            "example_model_metrics": model_metrics,
        }


metrics_service = MetricsService()
