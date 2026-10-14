"""Gemini keys, restricted transport, budget refusal and isolated RPC; no live inference."""

import copy
import json
from uuid import uuid4

import pytest
from pydantic import SecretStr
from rewind_core.contracts import RunMode
from rewind_replay.contracts import Intervention, TrialRequest
from rewind_replay.gemini import (
    GeminiBroker,
    GeminiError,
    GeminiHTTP,
    GeminiModelConfig,
    GeminiPolicy,
    decode_decision,
    load_key,
    provider_request,
)
from rewind_replay.gemini_runtime import execute_gemini
from rewind_replay.runtime import transform
from rewind_sandbox.fixtures import worlds


class FakeHTTP:
    """Unit adapter only. No test stub is an API/CLI provider path or live evidence."""

    def __init__(self):
        self.calls = []
        self.responses = []

    def call(self, path, body):
        self.calls.append((path, copy.deepcopy(body)))
        if path.endswith(":countTokens"):
            return {"totalTokens": 100}
        if self.responses:
            return copy.deepcopy(self.responses.pop(0))
        subject = json.loads(body["contents"][0]["parts"][0]["text"])
        value = {
            "actions": [],
            "summary": {k: subject["ticket"].get(k, "") for k in ("id", "issue", "resolution")},
        }
        return {
            "responseId": str(uuid4()),
            "modelVersion": "unit-provider-stub-not-real-evidence",
            "usageMetadata": {"promptTokenCount": 100, "totalTokenCount": 180},
            "candidates": [
                {"finishReason": "STOP", "content": {"parts": [{"text": json.dumps(value)}]}}
            ],
        }


def policy(**kwargs):
    return GeminiPolicy(billing_mode="declared_free_tier", declared_at="unit-test-only", **kwargs)


def test_secret_loader_opaque_labels_quotes_and_refusal(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    fake = "TEST_ONLY_OPAQUE.KEY_VALUE_1234567890"
    path = tmp_path / "unit-secret.txt"
    for value in (fake, f'"{fake}"', f'GEMINI_API_KEY="{fake}"', f"Gemini API Key: {fake}"):
        path.write_text(value, encoding="utf-8")
        loaded = load_key(path)
        assert loaded.get_secret_value() == fake
        assert fake not in str(loaded) and fake not in repr(loaded)
    for value in (fake + "\n" + fake, "short", "https://example.com/key", "x" * 4097):
        path.write_text(value, encoding="utf-8")
        with pytest.raises(GeminiError) as error:
            load_key(path)
        assert fake not in str(error.value)


def test_disabled_paid_zero_and_changed_binding_never_infer():
    config, http = GeminiModelConfig(), FakeHTTP()
    body = provider_request(worlds()["single"].subject, config, 1)
    for chosen in (GeminiPolicy(), GeminiPolicy(billing_mode="paid", declared_at="unit")):
        broker = GeminiBroker(config, chosen, http)
        with pytest.raises(GeminiError, match="authorised"):
            broker.infer(body, expected_request=body)
    assert http.calls == []
    broker = GeminiBroker(config, policy(), http)
    with pytest.raises(GeminiError, match="binding"):
        broker.infer({**body, "url": "https://evil.example"}, expected_request=body)
    assert http.calls == []


def test_request_token_cost_caps_and_no_automatic_retry():
    config = GeminiModelConfig()
    body = provider_request(worlds()["single"].subject, config, 1)
    for chosen in (
        policy(max_total_tokens=1),
        GeminiPolicy(billing_mode="paid", declared_at="unit", authorised_cost_usd=0.000001),
    ):
        http = FakeHTTP()
        with pytest.raises(GeminiError, match="budget_exhausted"):
            GeminiBroker(config, chosen, http).infer(body, expected_request=body)
        assert not any(p.endswith(":generateContent") for p, _ in http.calls)
    http = FakeHTTP()
    broker = GeminiBroker(config, policy(max_requests=1), http)
    broker.infer(body, expected_request=body)
    with pytest.raises(GeminiError, match="budget_exhausted"):
        broker.infer(body, expected_request=body)
    assert sum(p.endswith(":generateContent") for p, _ in http.calls) == 1
    assert broker.reserved_cost_usd == 0 and broker.records[0]["response_cache"] is False


def test_bad_responses_remain_invalid_and_duplicate_responses_are_refused():
    config, http = GeminiModelConfig(), FakeHTTP()
    body = provider_request(worlds()["single"].subject, config, 1)
    broker = GeminiBroker(config, policy(), http)
    first = broker.infer(body, expected_request=body)
    http.responses = [first]
    with pytest.raises(GeminiError, match="identity"):
        broker.infer(body, expected_request=body)
    assert broker.records[-1]["status"] == "invalid"
    assert broker.records[-1]["response"] == first
    bad = copy.deepcopy(first)
    bad["candidates"][0]["finishReason"] = "MAX_TOKENS"
    with pytest.raises(GeminiError):
        decode_decision(bad)
    bad["candidates"][0]["finishReason"] = "STOP"
    bad["candidates"][0]["content"]["parts"][0]["text"] = '{"actions":[],"summary":{}}'
    with pytest.raises(GeminiError):
        decode_decision(bad)


def test_transport_cannot_contact_arbitrary_endpoints():
    http = GeminiHTTP(SecretStr("TEST_ONLY_OPAQUE_KEY_123456789"))
    for path in ("https://evil.example", "/v1beta/models/other:generateContent", "/send_mail"):
        with pytest.raises(GeminiError, match="endpoint_refused"):
            http.call(path, {})


def test_capture_callback_happens_before_generation():
    config = GeminiModelConfig()
    events = []

    class OrderedHTTP(FakeHTTP):
        def call(self, path, body):
            if path.endswith(":generateContent"):
                assert events == ["reserved"]
            return super().call(path, body)

    broker = GeminiBroker(
        config,
        policy(),
        OrderedHTTP(),
        on_reserve=lambda _: events.append("reserved"),
        on_result=lambda _: events.append("result"),
    )
    body = provider_request(worlds()["single"].subject, config, 1)
    broker.infer(body, expected_request=body)
    assert events == ["reserved", "result"]


def test_invalid_tool_result_is_stored_and_sealed_without_success_counts(tmp_path, monkeypatch):
    from alembic import command
    from alembic.config import Config
    from rewind_capture.store import CaptureStore
    from rewind_capture.verify import verify
    from rewind_replay.container import ROOT
    from rewind_replay.gemini_cli import persist_trial

    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path))
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    store = CaptureStore(tmp_path)
    session_id = str(uuid4())
    store.create_session(session_id, {"mode": "remote_model"})
    result = {
        "validity": "invalid",
        "fresh_decision": True,
        "reason": "Tool arguments outside owned synthetic world",
        "model_response": {"summary": {}, "actions": []},
        "provider_response": {"responseId": "unit-only"},
        "attempts": [{"tool": "mail.send_email", "arguments": {"attachment": "unknown"}}],
    }
    persist_trial(store, session_id, result)
    bundle = store.export(session_id)
    assert verify(bundle, store.public)["valid"] is True
    assert bundle["seal"]["body"]["coverage"]["completed"] is False
    payloads = bundle["payloads"]
    outcomes = [
        payloads[e["body"]["payload_digest"]]
        for e in bundle["events"]
        if e["body"]["kind"] == "outcome"
    ]
    assert outcomes == [result]
    assert not any(e["body"]["kind"] == "tool_dispatched" for e in bundle["events"])
    assert "harmful_action_attempted" not in outcomes[0]
    store.engine.dispose()


def test_actual_container_rpc_has_fresh_transformed_requests_and_private_state():
    # Actual no-network Docker execution, but fake provider replies: transport evidence only.
    broker = GeminiBroker(GeminiModelConfig(), policy(), FakeHTTP())
    world = worlds()["single"]
    requests = [
        TrialRequest(
            world=world,
            mode=RunMode.REMOTE_MODEL,
            stochastic=True,
            seed=4471 + i,
            intervention=intervention,
        )
        for i, intervention in enumerate(
            [
                Intervention(),
                Intervention(kind="remove", targets=["comment-0"]),
                Intervention(kind="neutral_replace", targets=["comment-0"]),
            ]
        )
    ]
    results = [execute_gemini(request, broker) for request in requests]
    assert all(
        r["validity"] == "valid" and r["fresh_decision"] and r["task_success"] for r in results
    )
    assert len({r["request_digest"] for r in results}) == 3
    assert len({r["provider_response_id"] for r in results}) == 3
    assert all(r["outbox"] == [] and r["inference_interval"] is None for r in results)
    assert all(r["model_returned"] == "unit-provider-stub-not-real-evidence" for r in results)
    for request, result in zip(requests, results, strict=True):
        assert result["provider_request"] == provider_request(
            transform(request), broker.config, request.seed
        )
    assert "x-goog-api-key" not in json.dumps(broker.records)
