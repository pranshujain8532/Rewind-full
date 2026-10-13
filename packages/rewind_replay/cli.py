import argparse
import json
from pathlib import Path

from rewind_capture.verify import verify
from rewind_sandbox.schemas import World

from rewind_replay.container import execute, setup, verify_isolation
from rewind_replay.contracts import BatchRequest, Intervention, TrialRequest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["setup", "probe", "run"])
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--trusted-key", type=Path)
    parser.add_argument("--remove", nargs="*", default=[])
    args = parser.parse_args()
    if args.command == "setup":
        result = setup()
    elif args.command == "probe":
        result = verify_isolation()
    else:
        if not args.bundle or not args.trusted_key:
            parser.error("Replay requires bundle and independent trusted key")
        bundle = json.loads(args.bundle.read_bytes())
        checked = verify(bundle, args.trusted_key.read_bytes())
        if not checked["capture_complete"]:
            parser.error("Source capture insufficient or untrusted")
        source = next(
            bundle["payloads"][event["body"]["payload_digest"]]
            for event in bundle["events"]
            if event["body"]["kind"] == "initial_world"
        )
        mapping = {item["id"]: item["fixture_occurrence"] for item in bundle["occurrences"]}
        if not set(args.remove) <= mapping.keys():
            parser.error("Unknown captured occurrence UUID")
        trial = TrialRequest(
            world=World.model_validate(source),
            intervention=Intervention(
                kind="remove" if args.remove else "none",
                targets=[mapping[key] for key in args.remove],
            ),
        )
        result = execute(BatchRequest(trials=[trial]))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
