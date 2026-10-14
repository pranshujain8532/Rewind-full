"""A versioned owned neutral control is captured, not supplied as ranking truth."""

from rewind_sandbox.schemas import InputOccurrence, World

CONTROL_ID = "owned-neutral-control"
CONTROL_URI = "owned://rewind/neutral-control/v1"
CONTROL_TEXT = "Background: this is an owned synthetic support environment."


def controlled_world(world: World) -> World:
    subject = world.subject.model_copy(
        update={
            "inputs": [
                *world.subject.inputs,
                InputOccurrence(
                    occurrence_id=CONTROL_ID,
                    text=CONTROL_TEXT,
                    source_uri=CONTROL_URI,
                    origin="owner",
                ),
            ]
        }
    )
    return World.model_validate(
        {**world.model_dump(mode="json"), "subject": subject.model_dump(mode="json")}
    )


def has_control(world: World) -> bool:
    return any(
        item.occurrence_id == CONTROL_ID
        and item.origin == "owner"
        and item.source_uri == CONTROL_URI
        and item.text == CONTROL_TEXT
        for item in world.subject.inputs
    )
