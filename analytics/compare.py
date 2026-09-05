#!/usr/bin/env python3
"""Build a fair recent-window repository comparison snapshot."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import yaml

REQUIRED_DAILY_COLUMNS = {
    "date",
    "repository_id",
    "repository",
    "category",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
}

REQUIRED_ROLLUP_COLUMNS = {
    "date",
    "scope_type",
    "scope_id",
    "coverage_complete",
}

OUTPUT_COLUMNS = [
    "window_start",
    "window_end",
    "window_days",
    "repository_id",
    "repository",
    "category",
    "days_expected",
    "days_available",
    "coverage_pct",
    "coverage_complete",
    "clones_total",
    "views_total",
    "clones_unique_repo_day_sum",
    "views_unique_repo_day_sum",
    "clone_active_days",
    "view_active_days",
    "clone_only_days",
    "view_only_days",
    "mixed_days",
    "inactive_days",
    "clones_per_repo_day_unique",
    "views_per_repo_day_unique",
    "clone_to_view_ratio",
]


@dataclass(frozen=True)
class RepositoryPolicy:
    repository_id: str
    repository: str
    category: str


def _load_repositories(config_path: Path) -> list[RepositoryPolicy]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    repositories = config.get("repositories", [])

    selected: list[RepositoryPolicy] = []
    for item in repositories:
        if not item.get("collect", False):
            continue
        if not item.get("include_in_rollups", False):
            continue
        selected.append(
            RepositoryPolicy(
                repository_id=str(item["id"]),
                repository=str(item["repo"]),
                category=str(item["category"]),
            )
        )

    if not selected:
        raise ValueError("No repositories are enabled for repository comparison")

    return selected


def _read_daily_rows(input_path: Path) -> list[dict[str, str | int]]:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_DAILY_COLUMNS - fieldnames
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
                    "repository": row["repository"],
                    "category": row["category"],
                    "clones_total": int(row["clones_total"]),
                    "clones_unique": int(row["clones_unique"]),
                    "views_total": int(row["views_total"]),
                    "views_unique": int(row["views_unique"]),
                }
            )

    return rows


def _latest_complete_ecosystem_date(rollup_path: Path) -> date:
    with rollup_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_ROLLUP_COLUMNS - fieldnames
        if missing:
            raise ValueError(
                f"{rollup_path} is missing required columns: {sorted(missing)}"
            )

        complete_dates: list[date] = []
        for row in reader:
            if row["scope_type"] != "ecosystem" or row["scope_id"] != "ecosystem":
                continue
            is_complete = row["coverage_complete"].strip().lower() in {
                "true",
                "1",
                "yes",
            }
            if is_complete:
                complete_dates.append(date.fromisoformat(row["date"]))

    if not complete_dates:
        raise ValueError("No complete ecosystem day is available for comparison")

    return max(complete_dates)


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 2)


def build_comparison(
    config_path: Path,
    input_path: Path,
    rollup_path: Path,
    window_days: int = 14,
) -> list[dict[str, str | int | float | bool | None]]:
    if window_days < 1:
        raise ValueError("window_days must be at least 1")

    repositories = _load_repositories(config_path)
    daily_rows = _read_daily_rows(input_path)
    window_end = _latest_complete_ecosystem_date(rollup_path)
    window_start = window_end - timedelta(days=window_days - 1)

    expected_by_id = {repo.repository_id: repo for repo in repositories}
    rows_by_repository: dict[str, list[dict[str, str | int]]] = {
        repo.repository_id: [] for repo in repositories
    }

    for row in daily_rows:
        repository_id = str(row["repository_id"])
        policy = expected_by_id.get(repository_id)
        if policy is None:
            continue

        if str(row["repository"]) != policy.repository:
            raise ValueError(
                f"Repository mismatch for {repository_id}: "
                f"expected {policy.repository}, got {row['repository']}"
            )
        if str(row["category"]) != policy.category:
            raise ValueError(
                f"Category mismatch for {repository_id}: "
                f"expected {policy.category}, got {row['category']}"
            )

        row_date = date.fromisoformat(str(row["date"]))
        if window_start <= row_date <= window_end:
            rows_by_repository[repository_id].append(row)

    result: list[dict[str, str | int | float | bool | None]] = []
    for policy in repositories:
        repo_rows = rows_by_repository[policy.repository_id]
        days_available = len(repo_rows)
        coverage_pct = round(100.0 * days_available / window_days, 2)

        clones_total = sum(int(row["clones_total"]) for row in repo_rows)
        views_total = sum(int(row["views_total"]) for row in repo_rows)
        clones_unique_sum = sum(int(row["clones_unique"]) for row in repo_rows)
        views_unique_sum = sum(int(row["views_unique"]) for row in repo_rows)

        clone_active_days = 0
        view_active_days = 0
        clone_only_days = 0
        view_only_days = 0
        mixed_days = 0
        inactive_days = 0

        for row in repo_rows:
            has_clones = int(row["clones_total"]) > 0
            has_views = int(row["views_total"]) > 0

            clone_active_days += int(has_clones)
            view_active_days += int(has_views)

            if has_clones and has_views:
                mixed_days += 1
            elif has_clones:
                clone_only_days += 1
            elif has_views:
                view_only_days += 1
            else:
                inactive_days += 1

        result.append(
            {
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "window_days": window_days,
                "repository_id": policy.repository_id,
                "repository": policy.repository,
                "category": policy.category,
                "days_expected": window_days,
                "days_available": days_available,
                "coverage_pct": coverage_pct,
                "coverage_complete": days_available == window_days,
                "clones_total": clones_total,
                "views_total": views_total,
                "clones_unique_repo_day_sum": clones_unique_sum,
                "views_unique_repo_day_sum": views_unique_sum,
                "clone_active_days": clone_active_days,
                "view_active_days": view_active_days,
                "clone_only_days": clone_only_days,
                "view_only_days": view_only_days,
                "mixed_days": mixed_days,
                "inactive_days": inactive_days,
                "clones_per_repo_day_unique": _ratio(
                    clones_total, clones_unique_sum
                ),
                "views_per_repo_day_unique": _ratio(
                    views_total, views_unique_sum
                ),
                "clone_to_view_ratio": _ratio(clones_total, views_total),
            }
        )

    return result


def write_comparison(
    rows: Iterable[dict[str, str | int | float | bool | None]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a recent-window OrbitFabric repository comparison snapshot."
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
        "--rollups",
        type=Path,
        required=True,
        help="Daily rollup dataset used to select the latest complete day.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=14,
        help="Comparison window length in days.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/repository_comparison_latest.csv"),
        help="Output CSV path.",
    )
    args = parser.parse_args()

    rows = build_comparison(
        args.config,
        args.input,
        args.rollups,
        window_days=args.days,
    )
    write_comparison(rows, args.output)
    print(
        f"Wrote {len(rows)} repository comparison rows to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
