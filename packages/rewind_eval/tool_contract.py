"""The supported owned tool surface is pinned, not inferred from arbitrary capture."""


def supported_schemas(schemas: dict, world_version: str) -> bool:
    try:
        return _supported_schemas(schemas, world_version)
    except (AttributeError, TypeError, ValueError, KeyError):
        return False


def _supported_schemas(schemas: dict, world_version: str) -> bool:
    expected = {
        "ticket": ("ticket.read", {"ticket_id": "string", "delay_ms": "integer"}, {"ticket_id"}),
        "files": ("files.read", {"file_id": "string"}, {"file_id"}),
        "mail": (
            "mail.send_email",
            {"recipient": "string", "attachment": "string"},
            {"recipient", "attachment"},
        ),
    }
    if set(schemas) != set(expected) or world_version != "synthetic-support-v1":
        return False
    for kind, (name, properties, required) in expected.items():
        surface = schemas[kind]
        info = surface.get("meta", {}).get("io.modelcontextprotocol/serverInfo", {})
        tools = surface.get("tools", [])
        if (
            info.get("name") != f"rewind-owned-{kind}"
            or info.get("version") != world_version
            or surface.get("result_type") != "complete"
            or len(tools) != 1
        ):
            return False
        tool = tools[0]
        schema = tool.get("input_schema", {})
        if not set(schema) <= {"type", "properties", "required", "title"}:
            return False
        for key, property_schema in schema["properties"].items():
            allowed = {"type", "title", "default"} if key == "delay_ms" else {"type", "title"}
            if not set(property_schema) <= allowed:
                return False
            if key == "delay_ms" and property_schema.get("default", 0) != 0:
                return False
        observed = {key: value.get("type") for key, value in schema.get("properties", {}).items()}
        if (
            tool.get("name") != name
            or tool.get("description") != ""
            or tool.get("annotations") is not None
            or tool.get("execution") is not None
            or schema.get("type") != "object"
            or observed != properties
            or set(schema.get("required", [])) != required
            or tool.get("output_schema") is not None
        ):
            return False
    return True
