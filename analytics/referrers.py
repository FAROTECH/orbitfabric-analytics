#!/usr/bin/env python3
"""Aggregate GitHub Traffic referrer snapshots across official OrbitFabric repositories."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import yaml

SCHEMA_VERSION = 1


def _load_repositories(config_path: Path) -> list[dict[str, str]]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    repositories = config.get("repositories", [])
    selected: list[dict[str, str]] = []
    for item in repositories:
        if not item.get("collect", False):
            continue
        if not item.get("include_in_rollups", False):
            continue
        selected.append({"id": str(item["id"]), "repo": str(item["repo"])})
    if not selected:
        raise ValueError("No repositories are enabled for official rollups")
    return selected


def _latest_snapshot(path: Path) -> tuple[str, int, list[dict[str, object]]] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    snapshots = payload.get("snapshots")
    if not isinstance(snapshots, dict) or not snapshots:
        return None
    latest_date = max(str(day) for day in snapshots)
    rows = snapshots.get(latest_date)
    if not isinstance(rows, list):
        raise ValueError(f"Invalid referrer snapshot in {path}: {latest_date}")
    window_days = int(payload.get("window_days", 14))
    return latest_date, window_days, [row for row in rows if isinstance(row, dict)]


def build_referrer_aggregate(config_path: Path, data_root: Path) -> dict[str, object]:
    repositories = _load_repositories(config_path)
    totals: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "views": 0,
            "unique_visitors_repo_sum": 0,
            "repositories": 0,
        }
    )
    snapshot_dates: list[str] = []
    available = 0
    window_days = 14

    for repository in repositories:
        path = (
            data_root
            / repository["repo"]
            / "ghrs-data"
            / "referrers_history.json"
        )
        snapshot = _latest_snapshot(path)
        if snapshot is None:
            continue

        snapshot_date, repository_window_days, rows = snapshot
        available += 1
        snapshot_dates.append(snapshot_date)
        window_days = repository_window_days

        for row in rows:
            site = str(row.get("referrer", "")).strip()
            if not site:
                continue
            entry = totals[site]
            entry["views"] = int(entry["views"]) + int(row.get("views", 0))
            entry["unique_visitors_repo_sum"] = (
                int(entry["unique_visitors_repo_sum"])
                + int(row.get("unique_visitors", 0))
            )
            entry["repositories"] = int(entry["repositories"]) + 1

    rows = [
        {
            "site": site,
            "views": int(values["views"]),
            "unique_visitors_repo_sum": int(values["unique_visitors_repo_sum"]),
            "repositories": int(values["repositories"]),
        }
        for site, values in totals.items()
    ]
    rows.sort(
        key=lambda row: (
            -int(row["views"]),
            -int(row["unique_visitors_repo_sum"]),
            str(row["site"]).lower(),
        )
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "source": "github_traffic_popular_referrers",
        "window_days": window_days,
        "repositories_expected": len(repositories),
        "repositories_available": available,
        "snapshot_date_min": min(snapshot_dates) if snapshot_dates else None,
        "snapshot_date_max": max(snapshot_dates) if snapshot_dates else None,
        "sites_observed": len(rows),
        "rows": rows[:10],
    }


def write_referrer_aggregate(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate GitHub referrers across official OrbitFabric repositories."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build_referrer_aggregate(args.config, args.data_root)
    write_referrer_aggregate(payload, args.output)
    print(f"Wrote referrer aggregate to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
