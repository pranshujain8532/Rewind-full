import argparse
import json
from pathlib import Path

from rewind_capture.store import CaptureStore
from rewind_capture.verify import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["export", "verify"])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--session")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--trusted-key", type=Path)
    args = parser.parse_args()
    if args.command == "export":
        if not args.session:
            parser.error("Export requires --session")
        args.bundle.parent.mkdir(parents=True, exist_ok=True)
        bundle = CaptureStore(args.data).export(args.session)
        args.bundle.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    else:
        if not args.trusted_key:
            parser.error("Verification requires an independent --trusted-key")
        if args.bundle.stat().st_size > 8_000_000:
            parser.error("Bundle bound exceeded")
        result = verify(
            json.loads(args.bundle.read_text(encoding="utf-8")), args.trusted_key.read_bytes()
        )
        print(json.dumps(result, indent=2))
        if not result["valid"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
