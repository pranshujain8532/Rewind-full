"""Evidence export, independent verification and explicit original-attack regressions."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from rewind_ledger.bundle import MAX_BUNDLE_BYTES, bounded_json, verify_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--bundle", type=Path, required=True)
    verify.add_argument("--trusted-public-key", type=Path, required=True)
    export = commands.add_parser("record")
    export.add_argument("--investigation", required=True)
    export.add_argument("--output", type=Path, required=True)
    case = commands.add_parser("case")
    case.add_argument("--record", required=True)
    case.add_argument("--kind", choices=["behavioural", "containment"], default="behavioural")
    run = commands.add_parser("run")
    run.add_argument("--case", required=True)
    run.add_argument(
        "--fixed",
        choices=["vulnerable-v1", "behavioural-v1", "containment-v1", "deny-all-v1"],
        required=True,
    )
    run.add_argument("--output", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--left", required=True)
    compare.add_argument("--right", required=True)
    args = parser.parse_args()
    if args.command == "verify":
        # This path does not instantiate stores, create directories/keys or import the API.
        try:
            if args.bundle.stat().st_size > MAX_BUNDLE_BYTES:
                raise ValueError("bundle_too_large")
            if args.trusted_public_key.stat().st_size != 32:
                raise ValueError("trusted_key_invalid")
            checked = verify_bundle(
                bounded_json(args.bundle.read_bytes()), args.trusted_public_key.read_bytes()
            )
            print(checked.model_dump_json(indent=2))
            return 0 if checked.integrity_valid else 1
        except (ValueError, OSError):
            print(
                json.dumps(
                    {"integrity_valid": False, "reason": "corrupt_oversized_or_unavailable_input"}
                )
            )
            return 1
    from rewind_core.storage import data_directory
    from rewind_sandbox.fixtures import canonical

    from rewind_ledger.contracts import CaseRequest, RecordRequest, RegressionRequest
    from rewind_ledger.store import LedgerStore

    store = LedgerStore(data_directory())
    try:
        if args.command == "record":
            report = store.create_record(
                RecordRequest(investigation_id=args.investigation), str(uuid4())
            )
            with args.output.open("xb") as stream:
                stream.write(canonical(store.bundle(report["id"])))
            print(
                json.dumps(
                    {"record_id": report["id"], "evidence_status": report["evidence_status"]}
                )
            )
        elif args.command == "case":
            result = store.create_case(args.record, CaseRequest(kind=args.kind))
            print(
                json.dumps(
                    {k: result[k] for k in ("id", "record_id", "kind", "fixture_digest")}, indent=2
                )
            )
        elif args.command == "run":
            from rewind_ledger.worker import RegressionWorker

            snapshot = store.start(
                RegressionRequest(case_id=args.case, fixed_configuration=args.fixed), str(uuid4())
            )
            worker = RegressionWorker(store)
            while store.snapshot(snapshot.id).status == "queued" and worker.run_one():
                pass
            snapshot = store.snapshot(snapshot.id)
            if snapshot.manifest:
                with args.output.open("xb") as stream:
                    stream.write(canonical(store.run_bundle(snapshot.id)))
            print(snapshot.model_dump_json(indent=2))
            return 0 if snapshot.verdict == "pass" else 1
        else:
            print(json.dumps(store.compare(args.left, args.right), indent=2))
    except (ValueError, KeyError, OSError):
        print(
            json.dumps({"status": "inconclusive", "reason": "invalid_or_unavailable_ledger_input"})
        )
        return 1
    finally:
        store.engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
