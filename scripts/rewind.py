"""Cross-platform P0 entry points. Invoke from the repository root."""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UV_VERSION = "0.13.0"
WINDOWS = os.name == "nt"
BIN = "Scripts" if WINDOWS else "bin"
PYTHON = ROOT / ".venv" / BIN / ("python.exe" if WINDOWS else "python")
UV = ROOT / ".tools" / BIN / ("uv.exe" if WINDOWS else "uv")


def npm() -> str:
    executable = shutil.which("npm.cmd" if WINDOWS else "npm")
    if not executable:
        raise SystemExit("Install Node 22 (>=22.12) with npm 10 first.")
    return executable


def run(*args: str | Path, env: dict[str, str] | None = None) -> None:
    command = [str(arg) for arg in args]
    print("Running: " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def require_setup() -> None:
    if not PYTHON.exists():
        raise SystemExit("Run python scripts/rewind.py setup first.")


def setup() -> None:
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("Use Python 3.13; tested version is 3.13.12.")
    node = shutil.which("node")
    if not node:
        raise SystemExit("Install Node 22 (>=22.12) first.")
    node_version = subprocess.check_output([node, "--version"], text=True).strip()
    major, minor, *_ = map(int, node_version.lstrip("v").split("."))
    if major != 22 or minor < 12:
        raise SystemExit(f"Node {node_version} is outside the selected Node 22 range.")
    npm_major = int(subprocess.check_output([npm(), "--version"], text=True).split(".")[0])
    if npm_major != 10:
        raise SystemExit("Use npm 10 for this workspace lockfile.")
    if not UV.exists():
        run(sys.executable, "-m", "venv", ROOT / ".tools")
        tool_python = ROOT / ".tools" / BIN / ("python.exe" if WINDOWS else "python")
        run(tool_python, "-m", "pip", "install", f"uv=={UV_VERSION}")
    if subprocess.check_output([str(UV), "--version"], text=True).split()[1] != UV_VERSION:
        raise SystemExit(f"Use repository-local uv {UV_VERSION}.")
    run(UV, "sync", "--locked", "--cache-dir", ROOT / ".tools/uv-cache", "--python", sys.executable)
    run(
        npm(),
        "ci",
        "--ignore-scripts",
        "--no-audit",
        "--no-fund",
        "--cache",
        ROOT / ".tools/npm-cache",
    )
    migrate()
    run(PYTHON, ROOT / "scripts/export_schema.py", "--check")


def migrate() -> None:
    require_setup()
    run(PYTHON, "-m", "alembic", "upgrade", "head")


def api_command() -> list[str]:
    return [
        str(PYTHON),
        "-m",
        "uvicorn",
        "rewind_api.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]


def dev() -> None:
    require_setup()
    migrate()
    # The child runner executes npm.cmd; its process shares the terminal's Ctrl+C.
    children = [subprocess.Popen(api_command() + ["--reload"], cwd=ROOT)]
    try:
        children.append(subprocess.Popen([sys.executable, __file__, "web"], cwd=ROOT))
        print("Web: http://127.0.0.1:5173 · API: http://127.0.0.1:8000/api/health", flush=True)
        while all(child.poll() is None for child in children):
            try:
                children[0].wait(timeout=1)
            except subprocess.TimeoutExpired:
                continue
        raise SystemExit("A development server stopped; inspect its output above.")
    except KeyboardInterrupt:
        print("Stopping development servers.")
    finally:
        for child in children:
            if child.poll() is None:
                if WINDOWS:
                    # Stop only the process trees created by this invocation.
                    subprocess.run(
                        ["taskkill", "/PID", str(child.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()


def check() -> None:
    require_setup()
    evidence = ROOT / "artifacts/checks" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    evidence.mkdir(parents=True, exist_ok=True)
    run(PYTHON, "-m", "ruff", "check", ".")
    run(PYTHON, "-m", "ruff", "format", "--check", ".")
    run(PYTHON, "scripts/export_schema.py", "--check")
    run(PYTHON, "-m", "pytest", f"--junitxml={evidence / 'pytest.xml'}")
    run(npm(), "run", "build")
    run(PYTHON, "scripts/write_versions.py", "--check")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "setup",
            "dev",
            "api",
            "web",
            "migrate",
            "check",
            "schemas",
            "demo",
            "versions",
        ],
    )
    args = parser.parse_args()
    os.chdir(ROOT)
    if args.command == "setup":
        setup()
    elif args.command == "web":
        run(npm(), "run", "dev")
    else:
        require_setup()
        if args.command == "dev":
            dev()
        elif args.command == "api":
            run(*api_command())
        elif args.command == "migrate":
            migrate()
        elif args.command == "check":
            check()
        elif args.command == "schemas":
            run(PYTHON, "scripts/export_schema.py")
        elif args.command == "versions":
            run(PYTHON, "scripts/write_versions.py")
        elif args.command == "demo":
            run(PYTHON, "-m", "rewind_sandbox.cli", "run", "--scenario", "single")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
