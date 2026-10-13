import argparse
import json
from pathlib import Path

import anyio
from rewind_core.contracts import RunMode

from rewind_sandbox.fixtures import NAMES, generate, load_world
from rewind_sandbox.runner import run_world


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthetic support scenario, no external side effects"
    )
    parser.add_argument("command", choices=["generate", "run", "playback"])
    parser.add_argument("--recording", type=Path)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--scenario", choices=NAMES, default="single")
    parser.add_argument("--mode", choices=list(RunMode), default=RunMode.SIMULATED)
    parser.add_argument("--fixtures", type=Path, default=Path("fixtures"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/p1/runs"))
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(args.fixtures), indent=2))
    elif args.command == "playback":
        from rewind_sandbox.models import Playback
        from rewind_sandbox.schemas import RunResult

        if args.recording is None:
            parser.error("Playback requires --recording; no inference is run")
        print(
            Playback()
            .read(RunResult.model_validate_json(args.recording.read_bytes()))
            .model_dump_json(indent=2)
        )
    else:

        async def execute():
            from rewind_capture.store import CaptureStore

            result = await run_world(
                load_world(args.fixtures, args.scenario),
                args.output,
                RunMode(args.mode),
                capture_store=CaptureStore(args.data) if args.capture else None,
            )
            print(result.model_dump_json(indent=2))
            if args.capture:
                bundle_path = args.output / result.run_id / "bundle.json"
                bundle_path.write_text(
                    json.dumps(CaptureStore(args.data).export(result.run_id), indent=2),
                    encoding="utf-8",
                )

        anyio.run(execute)


if __name__ == "__main__":
    main()
