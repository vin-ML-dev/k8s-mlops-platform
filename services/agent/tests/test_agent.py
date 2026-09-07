"""Unit tests for deterministic Agent behavior.

Canary execution can be disabled at runtime, but its scoring logic remains
covered so the feature can be enabled again safely.
"""

from app.main import classify, pick_cycle, score_response


THRESHOLDS = {
    "p95_latency_seconds": 5.0,
    "backend_error_ratio": 0.10,
    "pod_restarts_15m": 3,
    "breaker_open_value": 1,
}


def schedule_config(canary_enabled: bool | None) -> dict:
    """Create the minimum configuration needed by pick_cycle()."""
    config = {
        "schedule": {
            "daily_hour_utc": -1,
            "canary_interval_seconds": 0,
        }
    }
    if canary_enabled is not None:
        config["canary"] = {"enabled": canary_enabled}
    return config


# ---- classify: deterministic health detection ----
def test_classify_healthy():
    state, anomalies = classify(
        {
            "gateway_reachable": True,
            "model_reachable": True,
            "model_replicas": 1,
            "p95_latency": 1.0,
            "error_ratio": 0.0,
            "pod_restarts": 0,
            "breaker_state": 0,
        },
        THRESHOLDS,
    )

    assert state == "healthy"
    assert anomalies == []


def test_classify_model_down_when_unreachable():
    state, anomalies = classify(
        {
            "gateway_reachable": True,
            "model_reachable": False,
            "model_replicas": 0,
        },
        THRESHOLDS,
    )

    assert state == "down"
    assert any(anomaly["key"] == "model_down" for anomaly in anomalies)


def test_classify_gateway_down():
    state, anomalies = classify({"gateway_reachable": False}, THRESHOLDS)

    assert state == "down"
    assert any(anomaly["key"] == "gateway_down" for anomaly in anomalies)


def test_classify_high_latency_is_degraded():
    state, anomalies = classify(
        {
            "gateway_reachable": True,
            "model_reachable": True,
            "model_replicas": 1,
            "p95_latency": 8.0,
            "error_ratio": 0.0,
            "pod_restarts": 0,
            "breaker_state": 0,
        },
        THRESHOLDS,
    )

    assert state == "degraded"
    assert any(anomaly["key"] == "high_latency" for anomaly in anomalies)


def test_classify_high_errors_is_degraded():
    state, anomalies = classify(
        {
            "gateway_reachable": True,
            "model_reachable": True,
            "model_replicas": 1,
            "p95_latency": 1.0,
            "error_ratio": 0.25,
            "pod_restarts": 0,
            "breaker_state": 0,
        },
        THRESHOLDS,
    )

    assert state == "degraded"
    assert any(anomaly["key"] == "high_errors" for anomaly in anomalies)


# ---- canary scheduling ----
def test_pick_cycle_skips_canary_when_disabled():
    cycle_type, last_canary, last_daily_day = pick_cycle(
        schedule_config(canary_enabled=False),
        last_canary=0.0,
        last_daily_day=-1,
    )

    assert cycle_type == "poll"
    assert last_canary == 0.0
    assert last_daily_day == -1


def test_pick_cycle_runs_canary_when_enabled():
    cycle_type, last_canary, last_daily_day = pick_cycle(
        schedule_config(canary_enabled=True),
        last_canary=0.0,
        last_daily_day=-1,
    )

    assert cycle_type == "canary"
    assert last_canary > 0.0
    assert last_daily_day == -1


def test_pick_cycle_defaults_to_enabled_when_flag_is_missing():
    cycle_type, _, _ = pick_cycle(
        schedule_config(canary_enabled=None),
        last_canary=0.0,
        last_daily_day=-1,
    )

    assert cycle_type == "canary"


# ---- score_response: canary scoring remains tested while disabled ----
def test_score_keyword_present():
    passed, _ = score_response(
        "Compound interest grows over time.",
        {"type": "keyword", "any": ["interest"]},
    )

    assert passed


def test_score_keyword_missing():
    passed, _ = score_response(
        "The weather is nice.",
        {"type": "keyword", "any": ["interest"]},
    )

    assert not passed


def test_score_refusal_detected():
    passed, _ = score_response(
        "I cannot predict future stock prices.",
        {"type": "refusal", "markers": ["cannot", "can't", "unable"]},
    )

    assert passed


def test_score_nonempty():
    passed, _ = score_response(
        "A sufficiently long answer here.",
        {"type": "nonempty", "min_chars": 10},
    )

    assert passed
