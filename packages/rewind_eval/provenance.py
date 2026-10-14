"""Observable input relationships only. No fixture keys, expected verdicts or labels."""

from collections import deque

from rewind_sandbox.outcomes import harmful
from rewind_sandbox.schemas import Action, World


def provenance(bundle: dict) -> dict:
    events = bundle["events"]
    payloads = bundle["payloads"]
    nodes, edges, targets = [], [], []
    world = World.model_validate(
        next(
            payloads[e["body"]["payload_digest"]]
            for e in events
            if e["body"]["kind"] == "initial_world"
        )
    )
    last_request = last_response = None
    requests = {}
    for event in events:
        body = event["body"]
        node_id = body["event_id"]
        kind = body["kind"]
        if kind not in {"model_request", "model_response", "tool_requested", "tool_dispatched"}:
            continue
        nodes.append({"id": node_id, "kind": kind, "seq": body["seq"]})
        payload = payloads[body["payload_digest"]]
        if kind == "model_request":
            last_request = node_id
            requests[node_id] = (body["seq"], payload["request"])
        elif kind == "model_response" and last_request:
            edges.append(
                {
                    "source": last_request,
                    "target": node_id,
                    "relationship": "observed_request_response",
                }
            )
            last_response = node_id
        elif kind == "tool_requested" and last_response:
            edges.append(
                {
                    "source": last_response,
                    "target": node_id,
                    "relationship": "observed_proposed_action",
                }
            )
            if harmful(Action.model_validate(payload), world):
                targets.append(node_id)
    anchor_seq = min((n["seq"] for n in nodes if n["id"] in targets), default=10**9)
    if not targets:
        targets = [n["id"] for n in nodes if n["kind"] == "model_response"]
    adjacency = {}
    for edge in edges:
        adjacency.setdefault(edge["source"], []).append(edge["target"])
    candidates = []
    for occurrence in bundle["occurrences"]:
        opaque_id = occurrence["id"]
        call = requests.get(occurrence["model_call_id"])
        present = bool(
            call
            and any(
                item["occurrence_id"] == occurrence["fixture_occurrence"]
                for item in call[1]["inputs"]
            )
        )
        before = bool(call and call[0] < anchor_seq)
        distance = None
        queue = deque([(occurrence["model_call_id"], 1)])
        visited = set()
        while queue:
            node, depth = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            if node in targets:
                distance = depth
                break
            queue.extend((child, depth + 1) for child in adjacency.get(node, []))
        features = {
            "present_in_model_input": int(present),
            "before_target": int(before),
            "external_origin": int(occurrence["origin"] == "external"),
            "graph_distance": distance,
            "proximity": 0 if distance is None else 1 / (1 + distance),
        }
        score = (
            4 * features["present_in_model_input"]
            + features["before_target"]
            + 2 * features["external_origin"]
            + features["proximity"]
        )
        nodes.append(
            {
                "id": opaque_id,
                "kind": "input_occurrence",
                "source_uri": occurrence["source_uri"],
                "origin": occurrence["origin"],
                "identity_verified": False,
                "blob_digest": occurrence["blob_digest"],
            }
        )
        if present:
            edges.append(
                {
                    "source": opaque_id,
                    "target": occurrence["model_call_id"],
                    "relationship": "captured_in_model_input",
                }
            )
        candidates.append(
            {
                "id": opaque_id,
                "target": occurrence["fixture_occurrence"],
                "origin": occurrence["origin"],
                "position": occurrence["position"],
                "score": score,
                "features": features,
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["position"], item["id"]))
    for rank, candidate in enumerate(candidates, 1):
        candidate["rank"] = rank
        candidate["selected"] = rank <= 8
        candidate["coverage"] = "untested" if rank <= 8 else "not_searched_candidate_limit"
        candidate["tested_subsets"] = []
    return {
        "schema_version": "1.0",
        "nodes": nodes,
        "edges": edges,
        "target_nodes": targets,
        "candidates": candidates,
        "ranking_formula": "4*present + before + 2*external + 1/(1+graph_distance)",
        "limitations": [
            "Observed relationships are not causal edges or private reasoning.",
            "Origin metadata does not verify a human identity.",
            "Low-ranked and untested candidates are not certified safe.",
        ],
    }
