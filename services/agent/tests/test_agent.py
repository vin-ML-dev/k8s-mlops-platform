<<<<<<< HEAD
"""Unit tests for deterministic Agent behavior.

Canary execution can be disabled at runtime, but its scoring logic remains
covered so the feature can be enabled again safely.
"""

from app.main import classify, pick_cycle, score_response

=======
"""Unit tests for deterministic Agent logic and Kubernetes inspection."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.main import Explainer, K8sInspector, classify, score_response
>>>>>>> origin/main

THRESHOLDS = {
    "p95_latency_seconds": 5.0,
    "backend_error_ratio": 0.10,
    "pod_restarts_15m": 3,
    "breaker_open_value": 1,
}


<<<<<<< HEAD
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

=======
def _healthy_signals(**overrides):
    signals = {
        "gateway_reachable": True,
        "model_reachable": True,
        "model_replicas": 1,
        "p95_latency": 1.0,
        "error_ratio": 0.0,
        "pod_restarts": 0,
        "breaker_state": 0,
    }
    signals.update(overrides)
    return signals


def _inspector_with_core(core):
    inspector = object.__new__(K8sInspector)
    inspector.namespace = "mlops"
    inspector._core = core
    return inspector


# Deterministic health detection
def test_classify_healthy():
    state, anomalies = classify(_healthy_signals(), THRESHOLDS)
>>>>>>> origin/main
    assert state == "healthy"
    assert anomalies == []


def test_classify_model_down_when_unreachable():
    state, anomalies = classify(
<<<<<<< HEAD
        {
            "gateway_reachable": True,
            "model_reachable": False,
            "model_replicas": 0,
        },
=======
        _healthy_signals(model_reachable=False, model_replicas=0),
>>>>>>> origin/main
        THRESHOLDS,
    )

    assert state == "down"
    assert any(anomaly["key"] == "model_down" for anomaly in anomalies)


def test_classify_gateway_down():
<<<<<<< HEAD
    state, anomalies = classify({"gateway_reachable": False}, THRESHOLDS)

=======
    state, anomalies = classify(
        _healthy_signals(gateway_reachable=False),
        THRESHOLDS,
    )
>>>>>>> origin/main
    assert state == "down"
    assert any(anomaly["key"] == "gateway_down" for anomaly in anomalies)


def test_classify_high_latency_is_degraded():
    state, anomalies = classify(
<<<<<<< HEAD
        {
            "gateway_reachable": True,
            "model_reachable": True,
            "model_replicas": 1,
            "p95_latency": 8.0,
            "error_ratio": 0.0,
            "pod_restarts": 0,
            "breaker_state": 0,
        },
=======
        _healthy_signals(p95_latency=8.0),
>>>>>>> origin/main
        THRESHOLDS,
    )

    assert state == "degraded"
    assert any(anomaly["key"] == "high_latency" for anomaly in anomalies)


def test_classify_high_errors_is_degraded():
    state, anomalies = classify(
<<<<<<< HEAD
        {
            "gateway_reachable": True,
            "model_reachable": True,
            "model_replicas": 1,
            "p95_latency": 1.0,
            "error_ratio": 0.25,
            "pod_restarts": 0,
            "breaker_state": 0,
        },
=======
        _healthy_signals(error_ratio=0.25),
>>>>>>> origin/main
        THRESHOLDS,
    )

    assert state == "degraded"
    assert any(anomaly["key"] == "high_errors" for anomaly in anomalies)


<<<<<<< HEAD
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
=======
# Deterministic canary scoring
>>>>>>> origin/main
def test_score_keyword_present():
    passed, _ = score_response(
        "Compound interest grows over time.",
        {"type": "keyword", "any": ["interest"]},
    )
<<<<<<< HEAD

=======
>>>>>>> origin/main
    assert passed


def test_score_keyword_missing():
    passed, _ = score_response(
        "The weather is nice.",
        {"type": "keyword", "any": ["interest"]},
    )
<<<<<<< HEAD

=======
>>>>>>> origin/main
    assert not passed


def test_score_refusal_detected():
    passed, _ = score_response(
        "I cannot predict future stock prices.",
        {"type": "refusal", "markers": ["cannot", "can't", "unable"]},
    )
<<<<<<< HEAD

=======
>>>>>>> origin/main
    assert passed


def test_score_nonempty():
    passed, _ = score_response(
        "A sufficiently long answer here.",
        {"type": "nonempty", "min_chars": 10},
    )
<<<<<<< HEAD

=======
>>>>>>> origin/main
    assert passed


# Read-only Kubernetes root-cause inspection
def test_k8s_inspector_is_disabled_when_client_is_unavailable(monkeypatch):
    monkeypatch.setattr("app.main._K8S_AVAILABLE", False)

    inspector = K8sInspector(namespace="mlops")

    assert not inspector.enabled
    assert inspector.inspect("model_down") == ""


def test_k8s_inspector_reads_previous_logs_and_warning_events():
    core = MagicMock(
        spec=[
            "list_namespaced_pod",
            "read_namespaced_pod_log",
            "list_namespaced_event",
        ]
    )
    terminated = SimpleNamespace(reason="OOMKilled", exit_code=137)
    container_status = SimpleNamespace(
        name="model",
        restart_count=2,
        last_state=SimpleNamespace(terminated=terminated),
    )
    pod = SimpleNamespace(
        metadata=SimpleNamespace(name="llama-cpp-abc"),
        status=SimpleNamespace(phase="Running", container_statuses=[container_status]),
    )
    core.list_namespaced_pod.return_value = SimpleNamespace(items=[pod])
    core.read_namespaced_pod_log.return_value = "process killed by memory limit"
    core.list_namespaced_event.return_value = SimpleNamespace(
        items=[
            SimpleNamespace(type="Normal", reason="Pulled", message="image pulled"),
            SimpleNamespace(
                type="Warning",
                reason="BackOff",
                message="restarting failed container",
            ),
        ]
    )
    inspector = _inspector_with_core(core)

    detail = inspector.inspect("model_down")

    assert "Pod llama-cpp-abc" in detail
    assert "OOMKilled (exit 137)" in detail
    assert "process killed by memory limit" in detail
    assert "Event: BackOff" in detail
    assert "image pulled" not in detail
    core.list_namespaced_pod.assert_called_once_with(
        "mlops",
        label_selector="app=llama-cpp",
    )
    core.read_namespaced_pod_log.assert_called_once_with(
        name="llama-cpp-abc",
        namespace="mlops",
        container="model",
        previous=True,
        tail_lines=30,
    )
    core.list_namespaced_event.assert_called_once_with("mlops")


def test_k8s_inspector_continues_when_previous_logs_are_missing():
    core = MagicMock(
        spec=[
            "list_namespaced_pod",
            "read_namespaced_pod_log",
            "list_namespaced_event",
        ]
    )
    terminated = SimpleNamespace(reason="Error", exit_code=1)
    container_status = SimpleNamespace(
        name="gateway",
        restart_count=1,
        last_state=SimpleNamespace(terminated=terminated),
    )
    pod = SimpleNamespace(
        metadata=SimpleNamespace(name="gateway-abc"),
        status=SimpleNamespace(phase="Running", container_statuses=[container_status]),
    )
    core.list_namespaced_pod.return_value = SimpleNamespace(items=[pod])
    core.read_namespaced_pod_log.side_effect = RuntimeError("previous log unavailable")
    core.list_namespaced_event.return_value = SimpleNamespace(items=[])
    inspector = _inspector_with_core(core)

    detail = inspector.inspect("gateway_down")

    assert "Pod gateway-abc" in detail
    assert "Error (exit 1)" in detail
    assert "inspection error" not in detail


def test_k8s_inspector_does_not_raise_when_api_fails():
    core = MagicMock(
        spec=[
            "list_namespaced_pod",
            "read_namespaced_pod_log",
            "list_namespaced_event",
        ]
    )
    core.list_namespaced_pod.side_effect = RuntimeError("API unavailable")
    inspector = _inspector_with_core(core)

    detail = inspector.inspect("model_down")

    assert detail == "(k8s inspection error: API unavailable)"


def test_explainer_adds_kubernetes_detail_to_llm_prompt(monkeypatch):
    explainer = Explainer(
        {
            "llm": {"backend": "template"},
            "kubernetes": {"namespace": "mlops"},
        }
    )
    explainer.k8s = MagicMock()
    explainer.k8s.inspect.return_value = (
        "Pod llama-cpp-abc: lastTerminated=OOMKilled (exit 137)"
    )
    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "The model container was OOMKilled.", True

    monkeypatch.setattr(explainer, "_generate", fake_generate)

    text, called = explainer.explain_incident(
        "down",
        [{"key": "model_down", "detail": "model unreachable"}],
        {"model_replicas": 0},
    )

    assert called
    assert text == "The model container was OOMKilled."
    assert "Kubernetes root-cause detail" in captured["prompt"]
    assert "OOMKilled (exit 137)" in captured["prompt"]
    explainer.k8s.inspect.assert_called_once_with("model_down")


def test_explainer_continues_when_kubernetes_inspection_fails(monkeypatch):
    explainer = Explainer(
        {
            "llm": {"backend": "template"},
            "kubernetes": {"namespace": "mlops"},
        }
    )
    explainer.k8s = MagicMock()
    explainer.k8s.inspect.side_effect = RuntimeError("API unavailable")

    def fake_generate(prompt):
        assert "Kubernetes root-cause detail" not in prompt
        return None, False

    monkeypatch.setattr(explainer, "_generate", fake_generate)

    text, called = explainer.explain_incident(
        "down",
        [{"key": "model_down", "detail": "model unreachable"}],
        {"model_replicas": 0},
    )

    assert not called
    assert text.startswith("DOWN: model unreachable")
