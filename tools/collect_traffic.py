#!/usr/bin/env python3
"""Collect GitHub traffic into the historical github-repo-stats CSV layout.

This collector intentionally separates credentials:
- GHRS_GITHUB_API_TOKEN reads traffic from target repositories.
- repository-scoped GITHUB_TOKEN is used by the workflow checkout/push path.

Only the views/clones aggregate consumed by OrbitFabric Analytics is updated.
Historical github-repo-stats artifacts remain untouched.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

FIELDNAMES = [
    "time_iso8601",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
]


def _normalize_timestamp(value: str) -> str:
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return instant.isoformat(sep=" ")


def _request_json(repository: str, metric: str, token: str) -> list[dict[str, object]]:
    request = Request(
        f"https://api.github.com/repos/{repository}/traffic/{metric}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "orbitfabric-analytics",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    rows = payload.get(metric)
    if not isinstance(rows, list):
        raise ValueError(f"Unexpected GitHub traffic response for {repository}/{metric}")
    return [row for row in rows if isinstance(row, dict)]


def _read_existing(path: Path) -> dict[str, dict[str, int | str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDNAMES) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        result: dict[str, dict[str, int | str]] = {}
        for row in reader:
            timestamp = str(row["time_iso8601"])
            result[timestamp] = {
                "time_iso8601": timestamp,
                "clones_total": int(row["clones_total"]),
                "clones_unique": int(row["clones_unique"]),
                "views_total": int(row["views_total"]),
                "views_unique": int(row["views_unique"]),
            }
        return result


def merge_metric(
    rows: dict[str, dict[str, int | str]],
    metric: str,
    snapshots: list[dict[str, object]],
) -> None:
    total_field = f"{metric}_total"
    unique_field = f"{metric}_unique"
    for item in snapshots:
        timestamp_raw = item.get("timestamp")
        if not isinstance(timestamp_raw, str):
            raise ValueError(f"Traffic {metric} item missing timestamp: {item}")
        timestamp = _normalize_timestamp(timestamp_raw)
        current = rows.setdefault(
            timestamp,
            {
                "time_iso8601": timestamp,
                "clones_total": 0,
                "clones_unique": 0,
                "views_total": 0,
                "views_unique": 0,
            },
        )
        current[total_field] = int(item.get("count", 0))
        current[unique_field] = int(item.get("uniques", 0))


def write_rows(path: Path, rows: dict[str, dict[str, int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = [rows[key] for key in sorted(rows)]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(ordered)


def collect(repository: str, output: Path, token: str) -> None:
    rows = _read_existing(output)
    merge_metric(rows, "clones", _request_json(repository, "clones", token))
    merge_metric(rows, "views", _request_json(repository, "views", token))
    write_rows(output, rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GitHub views/clones traffic.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--token-env", default="GHRS_GITHUB_API_TOKEN")
    args = parser.parse_args()

    token = os.getenv(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"{args.token_env} is not configured")

    output = (
        args.data_root
        / args.repository
        / "ghrs-data"
        / "views_clones_aggregate.csv"
    )
    collect(args.repository, output, token)
    print(f"Updated traffic dataset for {args.repository}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
