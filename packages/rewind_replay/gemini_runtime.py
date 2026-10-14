"""One bounded inference RPC per isolated trial. Parent alone holds credentials."""

import json
import queue
import subprocess
import threading
import time
from uuid import uuid4

from rewind_core.contracts import RunMode
from rewind_sandbox.fixtures import canonical, digest

from rewind_replay.contracts import TrialRequest
from rewind_replay.gemini import (
    GeminiBroker,
    GeminiError,
    GeminiModelConfig,
    decode_decision,
    provider_request,
)
from rewind_replay.runtime import run_trial, transform

MAX_FRAME_BYTES = 1_000_000


def worker_trial(envelope: dict, source, output) -> dict:
    if set(envelope) != {"operation", "trial", "configuration"}:
        raise GeminiError("remote_rpc_surface_refused")
    request = TrialRequest.model_validate(envelope["trial"])
    config = GeminiModelConfig.model_validate(envelope["configuration"])
    if request.mode != RunMode.REMOTE_MODEL or not request.stochastic:
        raise GeminiError("unsupported_remote_trial")
    exchange = {}

    def decide(subject):
        body = provider_request(subject, config, request.seed)
        nonce = str(uuid4())
        frame = {"type": "inference_request", "nonce": nonce, "body": body}
        output.write(canonical(frame).decode() + "\n")
        output.flush()
        line = source.readline(MAX_FRAME_BYTES + 1)
        if len(line.encode()) > MAX_FRAME_BYTES:
            raise GeminiError("inference_response_frame_too_large")
        response = json.loads(line)
        if response.get("nonce") != nonce or response.get("type") != "inference_response":
            raise GeminiError("inference_response_binding_failed")
        exchange.update(
            provider_request=body,
            provider_response=response["body"],
            model_requested=config.model,
            model_returned=response["body"]["modelVersion"],
            provider_response_id=response["body"]["responseId"],
            usage=response["body"]["usageMetadata"],
            model_config_digest=digest(config),
            provider="gemini",
        )
        return decode_decision(response["body"])

    result = run_trial(request, remote_decide=decide)
    return {**result, **exchange}


def execute_gemini(request: TrialRequest, broker: GeminiBroker, timeout: int = 60) -> dict:
    from rewind_replay.container import MANIFEST

    if request.mode != RunMode.REMOTE_MODEL or not request.stochastic:
        raise GeminiError("unsupported_remote_trial")
    runtime = json.loads(MANIFEST.read_bytes())
    if not runtime.get("isolation_verified"):
        raise GeminiError("replay_isolation_not_verified")
    # Reuse the exact supported sandbox flags; no bind mounts, keys, sockets or extra network.
    name = "rewind-gemini-" + str(uuid4())
    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        name,
        "--network",
        "none",
        "--dns",
        "127.0.0.1",
        "--read-only",
        "--user",
        "10001:10001",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--pids-limit",
        "64",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=32m,uid=10001,gid=10001,mode=0700",
        runtime["image_id"],
    ]
    envelope = {
        "operation": "gemini_trial",
        "trial": request.model_dump(mode="json"),
        "configuration": broker.config.model_dump(mode="json"),
    }
    if len(canonical(envelope)) > MAX_FRAME_BYTES:
        raise GeminiError("remote_trial_input_too_large")
    expected = provider_request(transform(request), broker.config, request.seed)
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    frames = queue.Queue(maxsize=4)

    def reader():
        try:
            while True:
                line = process.stdout.readline(MAX_FRAME_BYTES + 1)
                if not line:
                    frames.put(None, timeout=1)
                    return
                if len(line.encode()) > MAX_FRAME_BYTES:
                    frames.put({"type": "invalid_frame"}, timeout=1)
                    return
                frames.put(json.loads(line), timeout=1)
        except (ValueError, OSError, queue.Full):
            try:
                frames.put({"type": "invalid_frame"}, timeout=1)
            except queue.Full:
                pass

    deadline = time.monotonic() + timeout
    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()
    try:
        process.stdin.write(canonical(envelope).decode() + "\n")
        process.stdin.flush()
        calls = 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise GeminiError("remote_trial_timeout")
            try:
                frame = frames.get(timeout=remaining)
            except queue.Empty:
                raise GeminiError("remote_trial_timeout") from None
            if not isinstance(frame, dict):
                raise GeminiError("remote_worker_interrupted")
            if frame.get("type") == "inference_request":
                calls += 1
                if calls != 1 or set(frame) != {"type", "nonce", "body"}:
                    raise GeminiError("remote_rpc_surface_refused")
                response = broker.infer(frame["body"], expected_request=expected)
                process.stdin.write(
                    canonical(
                        {"type": "inference_response", "nonce": frame["nonce"], "body": response}
                    ).decode()
                    + "\n"
                )
                process.stdin.flush()
            elif frame.get("type") == "trial_result" and calls == 1:
                result = frame["result"]
                if (
                    result.get("mode") != RunMode.REMOTE_MODEL
                    or result.get("world_digest") != digest(request.world)
                    or result.get("seed") != request.seed
                    or result.get("provider_request") != expected
                    or result.get("provider_response_id")
                    != broker.records[-1]["response"]["responseId"]
                ):
                    raise GeminiError("remote_trial_result_binding_failed")
                process.stdin.close()
                process.wait(timeout=5)
                if process.returncode:
                    raise GeminiError("remote_worker_failed")
                return {
                    **result,
                    "environment": "isolated_sandbox_with_provider_broker",
                    "runtime_image_id": runtime["image_id"],
                    "network_exception": "parent provider-only HTTPS; sandbox has no network",
                    "evidence_status": "exploratory",
                    "inference_interval": None,
                }
            else:
                raise GeminiError("remote_rpc_surface_refused")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        subprocess.run(
            ["docker", "rm", "-f", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
        reader_thread.join(timeout=2)
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()
