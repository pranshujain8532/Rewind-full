"""Bounded byte-preserving stdio relay; SDK peers own the protocol lifecycle."""

import argparse
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from rewind_capture.store import CaptureStore

MAX_FRAME = 262144
MAX_LIFETIME_SECONDS = 60


def relay(kind: str) -> None:
    store = CaptureStore(Path(os.environ["REWIND_CAPTURE_DIR"]))
    session_id = os.environ["REWIND_SESSION_ID"]
    child = subprocess.Popen(
        [sys.executable, "-m", "rewind_sandbox.server", kind],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr.buffer,
        bufsize=0,
    )
    stopped = threading.Event()

    def stop():
        stopped.set()
        if child.poll() is None:
            child.terminate()

    def pump(source, target, direction):
        try:
            while not stopped.is_set():
                frame = source.readline(MAX_FRAME + 1)
                if not frame:
                    break
                if len(frame) > MAX_FRAME or not frame.endswith(b"\n"):
                    raise ValueError("frame_bound_or_framing")
                message = json.loads(frame)
                if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                    raise ValueError("unsupported_jsonrpc_frame")
                store.append(
                    session_id, "protocol_frame", {"direction": direction, "message": message}, kind
                )
                target.write(frame)
                target.flush()
        except (ValueError, OSError) as error:
            print(f"REWIND proxy stopped: {type(error).__name__}", file=sys.stderr)
        except Exception:
            print("REWIND proxy stopped: capture_failure", file=sys.stderr)
        finally:
            stop()

    lifetime = int(os.environ.get("REWIND_PROXY_LIFETIME", str(MAX_LIFETIME_SECONDS)))
    if not 1 <= lifetime <= MAX_LIFETIME_SECONDS:
        stop()
        raise ValueError("Proxy lifetime outside allowed bounds")
    timer = threading.Timer(lifetime, stop)
    timer.daemon = True
    timer.start()
    threading.Thread(
        target=pump, args=(sys.stdin.buffer, child.stdin, "client_to_server"), daemon=True
    ).start()
    try:
        pump(child.stdout, sys.stdout.buffer, "server_to_client")
    finally:
        stop()
        timer.cancel()
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=3)
        store.engine.dispose()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["ticket", "files", "mail"])
    relay(parser.parse_args().kind)


if __name__ == "__main__":
    main()
