"""Generate or check the backend-owned OpenAPI and TypeScript boundary."""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from rewind_api.app import app

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schema = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    with tempfile.TemporaryDirectory(prefix="rewind-schema-") as temporary:
        schema_path = Path(temporary) / "openapi.json"
        types_path = Path(temporary) / "api.d.ts"
        schema_path.write_text(schema, encoding="utf-8")
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        subprocess.run(
            [
                npm,
                "exec",
                "--workspace",
                "apps/web",
                "--",
                "openapi-typescript",
                str(schema_path),
                "--output",
                str(types_path),
            ],
            cwd=ROOT,
            check=True,
        )
        outputs = {
            ROOT / "schemas/openapi.json": schema,
            ROOT / "apps/web/src/generated/api.d.ts": types_path.read_text(encoding="utf-8"),
        }
        for path, contents in outputs.items():
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != contents:
                    raise SystemExit(
                        f"Schema drift: {path.relative_to(ROOT)}. Run the schemas command."
                    )
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")
        print("Shared schemas match." if args.check else "Shared schemas generated.")


if __name__ == "__main__":
    main()
