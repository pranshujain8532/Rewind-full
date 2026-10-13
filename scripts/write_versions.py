"""Record/check selected dependencies without reading credentials or model config."""

import argparse
import json
import platform
import shutil
import subprocess
from importlib.metadata import version
from pathlib import Path

from rewind_core.contracts import MCP_PROTOCOL_REVISION

ROOT = Path(__file__).resolve().parents[1]


def manifest() -> dict:
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0",
        "python": platform.python_version(),
        "node": subprocess.check_output(["node", "--version"], text=True).strip().lstrip("v"),
        "npm": subprocess.check_output(
            [shutil.which("npm.cmd") or "npm", "--version"], text=True
        ).strip(),
        "uv": "0.13.0",
        "python_dependencies": {
            name: version(name)
            for name in [
                "rewind",
                "fastapi",
                "pydantic",
                "sqlalchemy",
                "alembic",
                "uvicorn",
                "mcp",
                "pytest",
                "httpx",
                "ruff",
            ]
        },
        "web_dependencies": {
            name: metadata["version"]
            for name, metadata in lock["packages"].items()
            if name
            in [
                "node_modules/react",
                "node_modules/react-dom",
                "node_modules/vite",
                "node_modules/typescript",
                "node_modules/@vitejs/plugin-react",
                "node_modules/openapi-typescript",
                "node_modules/@playwright/test",
            ]
        },
        "mcp_protocol_revision": MCP_PROTOCOL_REVISION,
        "mcp_transport_scope": "stdio planned for P1; in-process SDK smoke only in P0",
        "models": {"local_model": "not configured", "remote_model": "not configured"},
        "replay_isolation": "unavailable; no verified worker exists",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    actual = manifest()
    path = ROOT / "versions.json"
    if args.check:
        expected = json.loads(path.read_text(encoding="utf-8"))
        # Supported runtime patch updates do not rewrite the selected/tested manifest.
        for key in ["python_dependencies", "web_dependencies", "mcp_protocol_revision", "uv"]:
            if actual[key] != expected[key]:
                raise SystemExit(f"Version manifest drift: {key}")
        print("Dependency manifest matches.")
    else:
        path.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8")
        print("Version manifest written.")


if __name__ == "__main__":
    main()
