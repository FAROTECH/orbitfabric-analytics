#!/usr/bin/env python3
"""Validate and normalize the OrbitFabric event registry."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml


def _load_yaml(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def _date_string(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        date.fromisoformat(value)
        return value
    raise ValueError(f"Invalid event date: {value!r}")


def build_event_registry(
    events_path: Path,
    taxonomy_path: Path,
    repositories_path: Path,
) -> dict[str, object]:
    events_doc = _load_yaml(events_path)
    taxonomy = _load_yaml(taxonomy_path)
    repositories_doc = _load_yaml(repositories_path)

    if int(events_doc.get("version", 0)) != 1:
        raise ValueError("Unsupported events registry version")
    if int(taxonomy.get("version", 0)) != 1:
        raise ValueError("Unsupported event taxonomy version")

    allowed_types = {str(item) for item in taxonomy.get("types", [])}
    allowed_channels = {str(item) for item in taxonomy.get("channels", [])}
    allowed_confidence = {
        str(item) for item in taxonomy.get("confidence_levels", [])
    }

    if not allowed_types or not allowed_channels or not allowed_confidence:
        raise ValueError("Event taxonomy must define types, channels and confidence levels")

    repository_ids = {
        str(item["id"])
        for item in repositories_doc.get("repositories", [])
        if isinstance(item, dict) and "id" in item
    }
    allowed_scopes = {"ecosystem", *repository_ids}

    raw_events = events_doc.get("events", [])
    if not isinstance(raw_events, list):
        raise ValueError("events must be a list")

    seen_ids: set[str] = set()
    normalized: list[dict[str, object]] = []

    for raw in raw_events:
        if not isinstance(raw, dict):
            raise ValueError("Each event must be a mapping")

        event_id = str(raw.get("id", "")).strip()
        if not event_id:
            raise ValueError("Event id is required")
        if event_id in seen_ids:
            raise ValueError(f"Duplicate event id: {event_id}")
        seen_ids.add(event_id)

        event_type = str(raw.get("type", "")).strip()
        channel = str(raw.get("channel", "")).strip()
        confidence = str(raw.get("confidence", "")).strip()
        label = str(raw.get("label", "")).strip()

        if event_type not in allowed_types:
            raise ValueError(f"Unknown event type for {event_id}: {event_type}")
        if channel not in allowed_channels:
            raise ValueError(f"Unknown event channel for {event_id}: {channel}")
        if confidence not in allowed_confidence:
            raise ValueError(
                f"Unknown confidence level for {event_id}: {confidence}"
            )
        if not label:
            raise ValueError(f"Event label is required for {event_id}")

        scope = raw.get("scope")
        if not isinstance(scope, list) or not scope:
            raise ValueError(f"Event scope must be a non-empty list for {event_id}")
        normalized_scope = [str(item).strip() for item in scope]
        unknown_scopes = sorted(set(normalized_scope) - allowed_scopes)
        if unknown_scopes:
            raise ValueError(
                f"Unknown event scope for {event_id}: {unknown_scopes}"
            )

        event: dict[str, object] = {
            "id": event_id,
            "date": _date_string(raw.get("date")),
            "type": event_type,
            "channel": channel,
            "scope": normalized_scope,
            "confidence": confidence,
            "label": label,
        }

        if raw.get("url"):
            event["url"] = str(raw["url"]).strip()
        if raw.get("notes"):
            event["notes"] = str(raw["notes"]).strip()

        normalized.append(event)

    normalized.sort(key=lambda item: (str(item["date"]), str(item["id"])))

    return {
        "schema_version": 1,
        "events": normalized,
    }


def write_event_registry(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and normalize OrbitFabric correlation events."
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/events_normalized.json"),
    )
    args = parser.parse_args()

    payload = build_event_registry(args.events, args.taxonomy, args.repositories)
    write_event_registry(payload, args.output)
    print(f"Wrote {len(payload['events'])} normalized events to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
