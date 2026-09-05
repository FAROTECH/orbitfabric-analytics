#!/usr/bin/env python3
"""Project normalized ecosystem events into the static dashboard payload."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _validate_dashboard(payload: dict[str, object]) -> list[dict[str, object]]:
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported dashboard schema")

    timeline = payload.get("timeline")
    if not isinstance(timeline, list) or not timeline:
        raise ValueError("Dashboard timeline is missing or empty")

    latest = payload.get("latest_complete_day")
    if not isinstance(latest, str):
        raise ValueError("Dashboard latest_complete_day is missing")
    date.fromisoformat(latest)

    rows: list[dict[str, object]] = []
    for point in timeline:
        if not isinstance(point, dict) or not isinstance(point.get("date"), str):
            raise ValueError("Dashboard timeline contains an invalid point")
        date.fromisoformat(str(point["date"]))
        rows.append(point)
    return rows


def _validate_events(payload: dict[str, object]) -> list[dict[str, object]]:
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported normalized event schema")

    events = payload.get("events")
    if not isinstance(events, list):
        raise ValueError("Normalized events payload is missing events")

    normalized: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Normalized event must be an object")

        event_id = event.get("id")
        event_date = event.get("date")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("Normalized event is missing id")
        if event_id in seen_ids:
            raise ValueError(f"Duplicate normalized event id: {event_id}")
        seen_ids.add(event_id)

        if not isinstance(event_date, str):
            raise ValueError(f"Event {event_id} is missing date")
        date.fromisoformat(event_date)

        normalized.append(dict(event))

    return sorted(normalized, key=lambda item: (str(item["date"]), str(item["id"])))


def project_events(
    dashboard: dict[str, object],
    normalized_events: dict[str, object],
) -> dict[str, object]:
    timeline = _validate_dashboard(dashboard)
    events = _validate_events(normalized_events)

    timeline_dates = [str(point["date"]) for point in timeline]
    timeline_date_set = set(timeline_dates)
    timeline_start = min(timeline_dates)
    timeline_end = max(timeline_dates)

    if timeline_end != dashboard["latest_complete_day"]:
        raise ValueError(
            "Dashboard timeline end does not match latest_complete_day"
        )

    events_by_date: dict[str, list[dict[str, object]]] = {}
    for event in events:
        events_by_date.setdefault(str(event["date"]), []).append(event)

    for point in timeline:
        day = str(point["date"])
        point["events"] = events_by_date.get(day, [])

    in_timeline = sum(1 for event in events if str(event["date"]) in timeline_date_set)
    pending = sum(1 for event in events if str(event["date"]) > timeline_end)
    before_timeline = sum(1 for event in events if str(event["date"]) < timeline_start)

    dashboard["events"] = events
    dashboard["event_context"] = {
        "timeline_start": timeline_start,
        "timeline_end": timeline_end,
        "events_total": len(events),
        "events_in_timeline": in_timeline,
        "events_pending": pending,
        "events_before_timeline": before_timeline,
    }
    return dashboard


def write_dashboard(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project normalized events into dashboard_data.json."
    )
    parser.add_argument("--dashboard", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    dashboard = _read_json(args.dashboard)
    events = _read_json(args.events)
    projected = project_events(dashboard, events)
    output = args.output or args.dashboard
    write_dashboard(projected, output)
    print(f"Projected {len(projected['events'])} events into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
