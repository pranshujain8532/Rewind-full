"""Append a phase report and concise restart context from verified evidence."""

import argparse
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument(
        "--status", choices=["VERIFIED", "IMPLEMENTED", "IN_PROGRESS", "BLOCKED"], required=True
    )
    args = parser.parse_args()
    report = args.report.read_text(encoding="utf-8")
    state = args.state.read_text(encoding="utf-8")
    if len(state.splitlines()) >= 150:
        raise SystemExit("Keep STATE under 150 lines")
    revision = subprocess.check_output(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "rev-parse",
            "HEAD",
        ],
        cwd=ROOT,
        text=True,
    ).strip()
    header = f"\n## {args.phase} — {datetime.now(UTC).isoformat()} — {args.status}\n\n"
    (ROOT / "docs/project/STATE.md").write_text(state, encoding="utf-8")
    (ROOT / "docs/project/HANDOFF.md").write_text(
        "# Handoff\n\nRead AGENTS, STATE, TASKS, relevant DECISIONS and the current prompt.\n"
        f"Checkpoint parent: `{revision}`. Latest continuation: {args.phase} {args.status}.\n\n"
        + state
        + "\n\n"
        + report,
        encoding="utf-8",
    )
    with (ROOT / "docs/project/SESSION-LOG.md").open("a", encoding="utf-8") as stream:
        stream.write(header + f"Starting revision: `{revision}`.\n\n" + report + "\n")
    board = ROOT / "docs/project/TASKS.md"
    lines = board.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"| {args.phase} |"):
            columns = line.split("|")
            columns[4] = f" {args.status} "
            columns[6] = f" docs/project/evidence/{args.phase}.md "
            lines[index] = "|".join(columns)
    board.write_text("\n".join(lines) + header + report + "\n", encoding="utf-8")
    (ROOT / "docs/project/evidence" / f"{args.phase}.md").write_text(
        f"# {args.phase} — {args.status}\n\nParent revision: `{revision}`.\n\n" + report,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
