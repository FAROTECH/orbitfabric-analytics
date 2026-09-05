#!/usr/bin/env python3
"""Build official OrbitFabric cross-repository daily rollups."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

REQUIRED_INPUT_COLUMNS = {
    "date",
    "repository_id",
    "category",
    "include_in_rollups",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
}

OUTPUT_COLUMNS = [
    "date",
    "scope_type",
    "scope_id",
    "repositories_expected",
    "repositories_available",
    "coverage_pct",
    "coverage_complete",
    "clones_total",
    "views_total",
    "clones_unique_repo_sum",
    "views_unique_repo_sum",
]


@dataclass(frozen=True)
class RollupRepository:
    repository_id: str
    category: str


def _load_rollup_repositories(config_path: Path) -> list[RollupRepository]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    repositories = config.get("repositories", [])

    selected: list[RollupRepository] = []
    for item in repositories:
        if not item.get("collect", False):
            continue
        if not item.get("include_in_rollups", False):
            continue
        selected.append(
            RollupRepository(
                repository_id=str(item["id"]),
                category=str(item["category"]),
            )
        )

    if not selected:
        raise ValueError("No repositories are enabled for official rollups")

    return selected


def _read_normalized_rows(input_path: Path) -> list[dict[str, str | int]]:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_INPUT_COLUMNS - fieldnames
        if missing:
            raise ValueError(
                f"{input_path} is missing required columns: {sorted(missing)}"
            )

        rows: list[dict[str, str | int]] = []
        seen_keys: set[tuple[str, str]] = set()

        for row in reader:
            key = (row["date"], row["repository_id"])
            if key in seen_keys:
                raise ValueError(
                    "Duplicate repository-day row in normalized dataset: "
                    f"{row['date']} / {row['repository_id']}"
                )
            seen_keys.add(key)

            rows.append(
                {
                    "date": row["date"],
                    "repository_id": row["repository_id"],
                    "category": row["category"],
                    "clones_total": int(row["clones_total"]),
                    "clones_unique": int(row["clones_unique"]),
                    "views_total": int(row["views_total"]),
                    "views_unique": int(row["views_unique"]),
                }
            )

    return rows


def build_rollups(
    config_path: Path, input_path: Path
) -> list[dict[str, str | int | float | bool]]:
    repositories = _load_rollup_repositories(config_path)
    normalized_rows = _read_normalized_rows(input_path)

    expected_by_id = {repo.repository_id: repo for repo in repositories}
    dates = sorted({str(row["date"]) for row in normalized_rows})

    metrics_by_key: dict[tuple[str, str], dict[str, int]] = {}
    for row in normalized_rows:
        repository_id = str(row["repository_id"])
        if repository_id not in expected_by_id:
            continue

        expected_category = expected_by_id[repository_id].category
        if str(row["category"]) != expected_category:
            raise ValueError(
                f"Category mismatch for {repository_id}: "
                f"expected {expected_category}, got {row['category']}"
            )

        metrics_by_key[(str(row["date"]), repository_id)] = {
            "clones_total": int(row["clones_total"]),
            "clones_unique": int(row["clones_unique"]),
            "views_total": int(row["views_total"]),
            "views_unique": int(row["views_unique"]),
        }

    scope_members: list[tuple[str, str, list[str]]] = [
        ("ecosystem", "ecosystem", [repo.repository_id for repo in repositories])
    ]

    category_members: dict[str, list[str]] = defaultdict(list)
    for repo in repositories:
        category_members[repo.category].append(repo.repository_id)

    for category in sorted(category_members):
        scope_members.append(("category", category, category_members[category]))

    rows: list[dict[str, str | int | float | bool]] = []
    for date in dates:
        for scope_type, scope_id, expected_ids in scope_members:
            available_metrics = [
                metrics_by_key[(date, repository_id)]
                for repository_id in expected_ids
                if (date, repository_id) in metrics_by_key
            ]

            repositories_expected = len(expected_ids)
            repositories_available = len(available_metrics)
            coverage_pct = round(
                100.0 * repositories_available / repositories_expected, 2
            )

            rows.append(
                {
                    "date": date,
                    "scope_type": scope_type,
                    "scope_id": scope_id,
                    "repositories_expected": repositories_expected,
                    "repositories_available": repositories_available,
                    "coverage_pct": coverage_pct,
                    "coverage_complete": repositories_available
                    == repositories_expected,
                    "clones_total": sum(
                        metrics["clones_total"] for metrics in available_metrics
                    ),
                    "views_total": sum(
                        metrics["views_total"] for metrics in available_metrics
                    ),
                    "clones_unique_repo_sum": sum(
                        metrics["clones_unique"] for metrics in available_metrics
                    ),
                    "views_unique_repo_sum": sum(
                        metrics["views_unique"] for metrics in available_metrics
                    ),
                }
            )

    return rows


def write_rollups(
    rows: Iterable[dict[str, str | int | float | bool]], output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build official OrbitFabric cross-repository daily rollups."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/repositories.yml"),
        help="Repository policy configuration.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Normalized repository-day dataset.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/ecosystem_rollups_daily.csv"),
        help="Output rollup CSV path.",
    )
    args = parser.parse_args()

    rows = build_rollups(args.config, args.input)
    write_rollups(rows, args.output)
    print(f"Wrote {len(rows)} daily rollup rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
