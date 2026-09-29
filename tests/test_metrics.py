from collections import Counter

from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_reports_request_errors_and_retrieval_success(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "REQUEST_LATENCIES", [])
    monkeypatch.setattr(metrics, "REQUEST_TTFT", [])
    monkeypatch.setattr(metrics, "REQUEST_COSTS", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_IN", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_OUT", [])
    monkeypatch.setattr(metrics, "ERRORS", Counter())
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "REQUESTS_SUCCEEDED", 0)
    monkeypatch.setattr(metrics, "RETRIEVAL_ATTEMPTS", 0)
    monkeypatch.setattr(metrics, "RETRIEVAL_SUCCEEDED", 0)
    monkeypatch.setattr(metrics, "QUALITY_SCORES", [])

    metrics.record_retrieval(True)
    metrics.record_request(100, 50, 0.001, 20, 10, 0.8)
    metrics.record_retrieval(False)
    metrics.record_error("RuntimeError")

    result = metrics.snapshot()

    assert result["traffic"] == 2
    assert result["requests_succeeded"] == 1
    assert result["requests_failed"] == 1
    assert result["error_rate_pct"] == 50.0
    assert result["retrieval_success_rate_pct"] == 50.0
