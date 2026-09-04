#!/usr/bin/env python3
"""Build the normalized OrbitFabric repository-day traffic dataset."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml

REQUIRED_INPUT_COLUMNS = {
    "time_iso8601",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
}

OUTPUT_COLUMNS = [
    "date",
    "repository_id",
    "repository",
    "category",
    "include_in_rollups",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
]


@dataclass(frozen=True)
class RepositoryPolicy:
    repository_id: str
    repository: str
    category: str
    include_in_rollups: bool


def _load_repository_policies(config_path: Path) -> list[RepositoryPolicy]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    repositories = config.get("repositories", [])

    policies: list[RepositoryPolicy] = []
    for item in repositories:
        if not item.get("collect", False):
            continue
        policies.append(
            RepositoryPolicy(
                repository_id=str(item["id"]),
                repository=str(item["repo"]),
                category=str(item["category"]),
                include_in_rollups=bool(item.get("include_in_rollups", False)),
            )
        )
    return policies


def _parse_date(value: str) -> str:
    return datetime.fromisoformat(value).date().isoformat()


def _read_repository_rows(
    data_root: Path, policy: RepositoryPolicy
) -> Iterable[dict[str, str | int | bool]]:
    source_path = (
        data_root
        / policy.repository
        / "ghrs-data"
        / "views_clones_aggregate.csv"
    )
    if not source_path.is_file():
        raise FileNotFoundError(
            f"Missing traffic dataset for {policy.repository}: {source_path}"
        )

    with source_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_INPUT_COLUMNS - fieldnames
        if missing:
            raise ValueError(
                f"{source_path} is missing required columns: {sorted(missing)}"
            )

        for row in reader:
            yield {
                "date": _parse_date(row["time_iso8601"]),
                "repository_id": policy.repository_id,
                "repository": policy.repository,
                "category": policy.category,
                "include_in_rollups": policy.include_in_rollups,
                "clones_total": int(row["clones_total"]),
                "clones_unique": int(row["clones_unique"]),
                "views_total": int(row["views_total"]),
                "views_unique": int(row["views_unique"]),
            }


def build_dataset(
    config_path: Path, data_root: Path
) -> list[dict[str, str | int | bool]]:
    rows: list[dict[str, str | int | bool]] = []
    for policy in _load_repository_policies(config_path):
        rows.extend(_read_repository_rows(data_root, policy))

    rows.sort(key=lambda row: (str(row["date"]), str(row["repository_id"])))
    return rows


def write_dataset(
    rows: Iterable[dict[str, str | int | bool]], output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a normalized repository-day OrbitFabric traffic dataset."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/repositories.yml"),
        help="Repository policy configuration.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        required=True,
        help="Root of the checked-out github-repo-stats branch.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/ecosystem_daily.csv"),
        help="Output CSV path.",
    )
    args = parser.parse_args()

    rows = build_dataset(args.config, args.data_root)
    write_dataset(rows, args.output)
    print(f"Wrote {len(rows)} repository-day rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
