import asyncio

import pytest
from app import config
from app.policy import AuthError, ValidationError, check_auth, validate_chat_request
from app.resilience import CircuitBreaker, CircuitOpenError, CircuitState, with_retries


def test_validate_caps_max_tokens():
    config.settings.MAX_TOKENS_CAP = 512
    body = validate_chat_request(
        {
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 99999,
        }
    )
    assert body["max_tokens"] == 512


def test_validate_rejects_empty_messages():
    with pytest.raises(ValidationError):
        validate_chat_request({"messages": []})


def test_validate_rejects_oversized_prompt():
    config.settings.MAX_PROMPT_CHARS = 10
    with pytest.raises(ValidationError):
        validate_chat_request(
            {"messages": [{"role": "user", "content": "x" * 50}]}
        )
    config.settings.MAX_PROMPT_CHARS = 8000


def test_auth_disabled_when_no_key():
    config.settings.GATEWAY_API_KEY = ""
    assert check_auth(None) == "anonymous"


def test_auth_rejects_bad_key():
    config.settings.GATEWAY_API_KEY = "secret123"
    with pytest.raises(AuthError):
        check_auth("Bearer wrong")


def test_auth_accepts_good_key():
    config.settings.GATEWAY_API_KEY = "secret123"
    client_id = check_auth("Bearer secret123")
    assert client_id and client_id != "anonymous"
    config.settings.GATEWAY_API_KEY = ""


def test_retries_then_succeeds():
    calls = {"n": 0}

    class Transient(Exception):
        pass

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise Transient()
        return "ok"

    result = asyncio.run(
        with_retries(
            flaky,
            max_attempts=3,
            backoff_s=0,
            retry_on=(Transient,),
        )
    )
    assert result == "ok" and calls["n"] == 3


def test_retries_give_up():
    class Transient(Exception):
        pass

    async def always_fail():
        raise Transient()

    with pytest.raises(Transient):
        asyncio.run(
            with_retries(
                always_fail,
                max_attempts=2,
                backoff_s=0,
                retry_on=(Transient,),
            )
        )


def test_circuit_opens_after_threshold():
    async def run():
        circuit_breaker = CircuitBreaker(fail_threshold=3, reset_timeout_s=10)

        async def boom():
            raise ValueError

        for _ in range(3):
            try:
                await circuit_breaker.call(boom)
            except ValueError:
                pass

        assert circuit_breaker.state == CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            await circuit_breaker.call(boom)

    asyncio.run(run())


def test_circuit_recovers_after_timeout():
    async def run():
        circuit_breaker = CircuitBreaker(fail_threshold=1, reset_timeout_s=0)

        async def boom():
            raise ValueError

        try:
            await circuit_breaker.call(boom)
        except ValueError:
            pass

        assert circuit_breaker.state == CircuitState.OPEN

        async def succeed():
            return "ok"

        result = await circuit_breaker.call(succeed)
        assert result == "ok" and circuit_breaker.state == CircuitState.CLOSED

    asyncio.run(run())
