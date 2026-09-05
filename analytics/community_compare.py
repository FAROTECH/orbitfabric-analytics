#!/usr/bin/env python3
"""Build latest-vs-previous comparisons for community stock snapshots."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

METRICS = [
    "stars_total",
    "forks_total",
    "open_issues_total",
    "open_pull_requests_total",
    "contributors_repo_count",
]

INPUT_FIELDS = [
    "date",
    "repository_id",
    "repository",
    "category",
    *METRICS,
]

OUTPUT_FIELDS = [
    "repository_id",
    "repository",
    "category",
    "current_date",
    "previous_date",
    "snapshot_gap_days",
    "comparable",
]
for metric in METRICS:
    OUTPUT_FIELDS.extend([metric, f"{metric}_delta"])


def read_history(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(INPUT_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"{path} contains no community snapshots")
    return rows


def parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def build_latest_comparison(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_repository: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        repository_id = row.get("repository_id", "")
        if not repository_id:
            raise ValueError("Community snapshot row is missing repository_id")
        date.fromisoformat(row["date"])
        by_repository[repository_id].append(row)

    output: list[dict[str, object]] = []
    for repository_id, history in by_repository.items():
        history.sort(key=lambda row: row["date"])
        current = history[-1]
        previous = history[-2] if len(history) >= 2 else None

        current_date = date.fromisoformat(current["date"])
        previous_date = date.fromisoformat(previous["date"]) if previous else None

        result: dict[str, object] = {
            "repository_id": repository_id,
            "repository": current["repository"],
            "category": current["category"],
            "current_date": current["date"],
            "previous_date": previous["date"] if previous else "",
            "snapshot_gap_days": (
                (current_date - previous_date).days if previous_date else ""
            ),
            "comparable": "true" if previous else "false",
        }

        for metric in METRICS:
            current_value = parse_optional_int(current.get(metric))
            previous_value = parse_optional_int(previous.get(metric)) if previous else None
            result[metric] = "" if current_value is None else current_value
            result[f"{metric}_delta"] = (
                ""
                if current_value is None or previous_value is None
                else current_value - previous_value
            )

        output.append(result)

    output.sort(key=lambda row: str(row["repository_id"]))
    return output


def write_comparison(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build latest community stock deltas for OrbitFabric repositories."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = build_latest_comparison(read_history(args.input))
    write_comparison(args.output, rows)
    comparable = sum(1 for row in rows if row["comparable"] == "true")
    print(
        f"Wrote {len(rows)} community comparisons to {args.output}; "
        f"{comparable} have a previous snapshot"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
