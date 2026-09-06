"""Unit tests for the agent's deterministic detection logic (classify) and the
canary scoring (score_response). These are pure functions — no cluster, no LLM,
no network — so they run in CI without any live dependencies."""
from app.main import classify, score_response

THRESHOLDS = {
    "p95_latency_seconds": 5.0,
    "backend_error_ratio": 0.10,
    "pod_restarts_15m": 3,
    "breaker_open_value": 1,
}


# ---- classify: deterministic health detection ----
def test_classify_healthy():
    state, anomalies = classify(
        {"gateway_reachable": True, "model_reachable": True, "model_replicas": 1,
         "p95_latency": 1.0, "error_ratio": 0.0, "pod_restarts": 0, "breaker_state": 0},
        THRESHOLDS,
    )
    assert state == "healthy" and anomalies == []

def test_classify_model_down_when_unreachable():
    state, anomalies = classify(
        {"gateway_reachable": True, "model_reachable": False, "model_replicas": 0},
        THRESHOLDS,
    )
    assert state == "down"
    assert any(a["key"] == "model_down" for a in anomalies)

def test_classify_gateway_down():
    state, anomalies = classify({"gateway_reachable": False}, THRESHOLDS)
    assert state == "down"
    assert any(a["key"] == "gateway_down" for a in anomalies)

def test_classify_high_latency_is_degraded():
    state, anomalies = classify(
        {"gateway_reachable": True, "model_reachable": True, "model_replicas": 1,
         "p95_latency": 8.0, "error_ratio": 0.0, "pod_restarts": 0, "breaker_state": 0},
        THRESHOLDS,
    )
    assert state == "degraded"
    assert any(a["key"] == "high_latency" for a in anomalies)

def test_classify_high_errors_is_degraded():
    state, anomalies = classify(
        {"gateway_reachable": True, "model_reachable": True, "model_replicas": 1,
         "p95_latency": 1.0, "error_ratio": 0.25, "pod_restarts": 0, "breaker_state": 0},
        THRESHOLDS,
    )
    assert state == "degraded"
    assert any(a["key"] == "high_errors" for a in anomalies)


# ---- score_response: canary scoring ----
def test_score_keyword_present():
    passed, _ = score_response("Compound interest grows over time.",
                               {"type": "keyword", "any": ["interest"]})
    assert passed

def test_score_keyword_missing():
    passed, _ = score_response("The weather is nice.",
                               {"type": "keyword", "any": ["interest"]})
    assert not passed

def test_score_refusal_detected():
    passed, _ = score_response("I cannot predict future stock prices.",
                               {"type": "refusal", "markers": ["cannot", "can't", "unable"]})
    assert passed

def test_score_nonempty():
    passed, _ = score_response("A sufficiently long answer here.",
                               {"type": "nonempty", "min_chars": 10})
    assert passed
