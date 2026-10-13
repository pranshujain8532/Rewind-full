"""Index local P0 engineering evidence. This is not a signed agent record."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/p0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = []
    for directory in [
        "packages",
        "services",
        "apps/web/src",
        "migrations",
        "scripts",
        "tests",
        "schemas",
    ]:
        paths.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.is_file()
            and path.suffix in {".py", ".ts", ".tsx", ".css", ".json", ".cjs"}
            and "__pycache__" not in path.parts
        )
    paths.extend(
        ROOT / name
        for name in [
            "pyproject.toml",
            "uv.lock",
            "package.json",
            "package-lock.json",
            "versions.json",
            "playwright.config.ts",
            "alembic.ini",
            "apps/web/package.json",
            "apps/web/tsconfig.json",
            "apps/web/vite.config.ts",
            "apps/web/index.html",
        ]
    )
    sources = {
        str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in sorted(set(paths))
    }
    source_digest = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    junit = ET.parse(OUTPUT / "pytest.xml")
    suites = list(junit.iter("testsuite"))
    browser = json.loads((OUTPUT / "playwright.json").read_text(encoding="utf-8"))
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    head = subprocess.run(
        [*git, "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True
    )
    status = subprocess.check_output([*git, "status", "--short"], cwd=ROOT, text=True)
    evidence = {
        "kind": "p0_engineering_checks_not_agent_experiments",
        "recorded_at": datetime.now(UTC).isoformat(),
        "git_revision": head.stdout.strip()
        if head.returncode == 0
        else "no HEAD; initial uncommitted repository",
        "git_dirty": bool(status.strip()),
        "source_snapshot_sha256": source_digest,
        "source_sha256": sources,
        "pytest": {
            key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
            for key in ["tests", "failures", "errors", "skipped"]
        },
        "playwright": browser["stats"],
        "artifact_sha256": {
            path.name: digest(path)
            for path in sorted(OUTPUT.iterdir())
            if path.is_file() and path.name != "evidence-manifest.json"
        },
        "limitations": [
            "Not a clean-machine install; local locked reinstall was verified.",
            "Linux/WSL/container execution and replay isolation are not_run.",
            "No agent runs, fresh model trials, signed records or security certification.",
        ],
    }
    (OUTPUT / "evidence-manifest.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "source_snapshot_sha256": source_digest,
                "pytest": evidence["pytest"],
                "playwright": evidence["playwright"],
                "git_revision": evidence["git_revision"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
