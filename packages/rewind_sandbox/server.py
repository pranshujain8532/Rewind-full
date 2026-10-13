"""Three stdio mock servers. Protocol stdout belongs exclusively to the SDK."""

import argparse
import json
import os
from pathlib import Path

from mcp.server import MCPServer

from rewind_sandbox.schemas import World


def create_server(kind: str, world: World, outbox: Path) -> MCPServer:
    server = MCPServer(f"rewind-owned-{kind}", version=world.version)
    if kind == "ticket":

        @server.tool(name="ticket.read")
        def read_ticket(ticket_id: str) -> dict:
            if ticket_id != world.subject.ticket["id"]:
                raise ValueError("Unknown synthetic ticket")
            return {
                "ticket": world.subject.ticket,
                "inputs": [item.model_dump(mode="json") for item in world.subject.inputs],
            }
    elif kind == "files":

        @server.tool(name="files.read")
        def read_file(file_id: str) -> dict:
            if file_id not in world.files:
                raise ValueError("Unknown synthetic file")
            return world.files[file_id]
    elif kind == "mail":

        @server.tool(name="mail.send_email")
        def send_email(recipient: str, attachment: str) -> dict:
            if not recipient.casefold().endswith(".example") or len(recipient) > 200:
                raise ValueError("Only reserved .example addresses allowed")
            if attachment not in world.files:
                raise ValueError("Unknown synthetic attachment")
            record = {
                "recipient": recipient,
                "attachment": attachment,
                "rows": world.files[attachment]["rows"],
                "sink": "local_synthetic_outbox",
            }
            outbox.parent.mkdir(parents=True, exist_ok=True)
            with outbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
            return {
                "accepted": True,
                "sink": "local_synthetic_outbox",
                "synthetic_rows": len(record["rows"]),
            }
    else:
        raise ValueError("Unsupported mock server")
    return server


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["ticket", "files", "mail"])
    args = parser.parse_args()
    world = World.model_validate_json(Path(os.environ["REWIND_WORLD_FILE"]).read_bytes())
    create_server(args.kind, world, Path(os.environ["REWIND_OUTBOX_FILE"])).run(transport="stdio")


if __name__ == "__main__":
    main()
