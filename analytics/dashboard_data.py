#!/usr/bin/env python3
"""Build the presentation-ready payload consumed by the static dashboard."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

REQUIRED_ROLLUP_COLUMNS = {
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
}

REQUIRED_COMPARISON_COLUMNS = {
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
}

REQUIRED_DAILY_COLUMNS = {
    "date",
    "repository_id",
    "clones_total",
    "clones_unique",
    "views_total",
    "views_unique",
}


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _as_optional_float(value: str) -> float | None:
    value = value.strip()
    return None if value == "" else float(value)


def _read_rollups(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_ROLLUP_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        rows: list[dict[str, object]] = []
        for row in reader:
            rows.append(
                {
                    "date": row["date"],
                    "scope_type": row["scope_type"],
                    "scope_id": row["scope_id"],
                    "repositories_expected": int(row["repositories_expected"]),
                    "repositories_available": int(row["repositories_available"]),
                    "coverage_pct": float(row["coverage_pct"]),
                    "coverage_complete": _as_bool(row["coverage_complete"]),
                    "clones_total": int(row["clones_total"]),
                    "views_total": int(row["views_total"]),
                    "clones_unique_repo_sum": int(row["clones_unique_repo_sum"]),
                    "views_unique_repo_sum": int(row["views_unique_repo_sum"]),
                }
            )
    return rows


def _read_comparison(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COMPARISON_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        rows: list[dict[str, object]] = []
        for row in reader:
            rows.append(
                {
                    "window_start": row["window_start"],
                    "window_end": row["window_end"],
                    "window_days": int(row["window_days"]),
                    "repository_id": row["repository_id"],
                    "repository": row["repository"],
                    "category": row["category"],
                    "days_expected": int(row["days_expected"]),
                    "days_available": int(row["days_available"]),
                    "coverage_pct": float(row["coverage_pct"]),
                    "coverage_complete": _as_bool(row["coverage_complete"]),
                    "clones_total": int(row["clones_total"]),
                    "views_total": int(row["views_total"]),
                    "clones_unique_repo_day_sum": int(
                        row["clones_unique_repo_day_sum"]
                    ),
                    "views_unique_repo_day_sum": int(
                        row["views_unique_repo_day_sum"]
                    ),
                    "clone_active_days": int(row["clone_active_days"]),
                    "view_active_days": int(row["view_active_days"]),
                    "clone_only_days": int(row["clone_only_days"]),
                    "view_only_days": int(row["view_only_days"]),
                    "mixed_days": int(row["mixed_days"]),
                    "inactive_days": int(row["inactive_days"]),
                    "clones_per_repo_day_unique": _as_optional_float(
                        row["clones_per_repo_day_unique"]
                    ),
                    "views_per_repo_day_unique": _as_optional_float(
                        row["views_per_repo_day_unique"]
                    ),
                    "clone_to_view_ratio": _as_optional_float(
                        row["clone_to_view_ratio"]
                    ),
                }
            )
    return rows


def _read_daily(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_DAILY_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        rows: list[dict[str, object]] = []
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
                    "clones_total": int(row["clones_total"]),
                    "clones_unique": int(row["clones_unique"]),
                    "views_total": int(row["views_total"]),
                    "views_unique": int(row["views_unique"]),
                }
            )
    return rows


def _compact_scope(row: dict[str, object]) -> dict[str, object]:
    return {
        "scope_id": row["scope_id"],
        "repositories_expected": row["repositories_expected"],
        "repositories_available": row["repositories_available"],
        "coverage_pct": row["coverage_pct"],
        "coverage_complete": row["coverage_complete"],
        "clones_total": row["clones_total"],
        "views_total": row["views_total"],
        "clones_unique_repo_sum": row["clones_unique_repo_sum"],
        "views_unique_repo_sum": row["views_unique_repo_sum"],
    }


def _metric_delta(current: int, previous: int) -> dict[str, object]:
    absolute = current - previous
    if previous == 0:
        if current == 0:
            pct: float | None = 0.0
            state = "unchanged"
        else:
            pct = None
            state = "new"
    else:
        pct = round(100.0 * absolute / previous, 1)
        if absolute > 0:
            state = "increase"
        elif absolute < 0:
            state = "decrease"
        else:
            state = "unchanged"

    return {
        "current": current,
        "previous": previous,
        "absolute": absolute,
        "pct": pct,
        "state": state,
    }


def _overview_delta(
    current: dict[str, object],
    previous: dict[str, object],
    reference_day: str,
) -> dict[str, object]:
    return {
        "reference_day": reference_day,
        "clones_total": _metric_delta(
            int(current["clones_total"]), int(previous["clones_total"])
        ),
        "views_total": _metric_delta(
            int(current["views_total"]), int(previous["views_total"])
        ),
        "clones_unique_repo_sum": _metric_delta(
            int(current["clones_unique_repo_sum"]),
            int(previous["clones_unique_repo_sum"]),
        ),
        "views_unique_repo_sum": _metric_delta(
            int(current["views_unique_repo_sum"]),
            int(previous["views_unique_repo_sum"]),
        ),
    }


def _repository_snapshot_delta(
    current: dict[str, object],
    previous_rows: list[dict[str, object]],
    window_days: int,
) -> dict[str, object]:
    days_available = len(previous_rows)
    coverage_pct = round(100.0 * days_available / window_days, 2)
    comparable = bool(current["coverage_complete"]) and days_available == window_days

    result: dict[str, object] = {
        "comparable": comparable,
        "previous_days_available": days_available,
        "previous_coverage_pct": coverage_pct,
    }
    if not comparable:
        return result

    previous_clones = sum(int(row["clones_total"]) for row in previous_rows)
    previous_views = sum(int(row["views_total"]) for row in previous_rows)
    previous_clones_unique = sum(int(row["clones_unique"]) for row in previous_rows)
    previous_views_unique = sum(int(row["views_unique"]) for row in previous_rows)

    result.update(
        {
            "clones_total": _metric_delta(
                int(current["clones_total"]), previous_clones
            ),
            "views_total": _metric_delta(
                int(current["views_total"]), previous_views
            ),
            "clones_unique_repo_day_sum": _metric_delta(
                int(current["clones_unique_repo_day_sum"]),
                previous_clones_unique,
            ),
            "views_unique_repo_day_sum": _metric_delta(
                int(current["views_unique_repo_day_sum"]),
                previous_views_unique,
            ),
        }
    )
    return result


def build_dashboard_payload(
    rollup_path: Path,
    comparison_path: Path,
    daily_path: Path | None = None,
) -> dict[str, object]:
    rollups = _read_rollups(rollup_path)
    comparison = _read_comparison(comparison_path)
    daily_rows = _read_daily(daily_path) if daily_path is not None else []

    complete_ecosystem_rows = sorted(
        (
            row
            for row in rollups
            if row["scope_type"] == "ecosystem"
            and row["scope_id"] == "ecosystem"
            and bool(row["coverage_complete"])
        ),
        key=lambda row: date.fromisoformat(str(row["date"])),
    )
    if not complete_ecosystem_rows:
        raise ValueError("No complete ecosystem day is available for the dashboard")

    latest_ecosystem = complete_ecosystem_rows[-1]
    latest_date = date.fromisoformat(str(latest_ecosystem["date"]))
    latest_day = latest_date.isoformat()

    previous_ecosystem = (
        complete_ecosystem_rows[-2] if len(complete_ecosystem_rows) >= 2 else None
    )
    previous_complete_day = (
        str(previous_ecosystem["date"]) if previous_ecosystem is not None else None
    )

    latest_categories = sorted(
        (
            _compact_scope(row)
            for row in rollups
            if row["date"] == latest_day and row["scope_type"] == "category"
        ),
        key=lambda item: str(item["scope_id"]),
    )

    dates = sorted(
        {
            str(row["date"])
            for row in rollups
            if date.fromisoformat(str(row["date"])) <= latest_date
        }
    )
    timeline: list[dict[str, object]] = []
    for day in dates:
        day_rows = [row for row in rollups if row["date"] == day]
        ecosystem = next(
            (
                _compact_scope(row)
                for row in day_rows
                if row["scope_type"] == "ecosystem"
                and row["scope_id"] == "ecosystem"
            ),
            None,
        )
        categories = {
            str(row["scope_id"]): _compact_scope(row)
            for row in day_rows
            if row["scope_type"] == "category"
        }
        timeline.append(
            {
                "date": day,
                "ecosystem": ecosystem,
                "categories": categories,
            }
        )

    if not comparison:
        raise ValueError("Repository comparison dataset is empty")

    window_keys = {
        (
            str(row["window_start"]),
            str(row["window_end"]),
            int(row["window_days"]),
        )
        for row in comparison
    }
    if len(window_keys) != 1:
        raise ValueError("Repository comparison rows do not share one common window")

    window_start, window_end, window_days = next(iter(window_keys))
    if window_end != latest_day:
        raise ValueError(
            "Repository comparison is not anchored to the latest complete ecosystem day"
        )

    repositories = sorted(comparison, key=lambda row: str(row["repository_id"]))

    previous_window_start: str | None = None
    previous_window_end: str | None = None
    if previous_complete_day is not None and daily_path is not None:
        previous_end_date = date.fromisoformat(previous_complete_day)
        previous_start_date = previous_end_date - timedelta(days=window_days - 1)
        previous_window_start = previous_start_date.isoformat()
        previous_window_end = previous_end_date.isoformat()

        for repository in repositories:
            repository_id = str(repository["repository_id"])
            previous_rows = [
                row
                for row in daily_rows
                if str(row["repository_id"]) == repository_id
                and previous_start_date
                <= date.fromisoformat(str(row["date"]))
                <= previous_end_date
            ]
            repository["delta"] = _repository_snapshot_delta(
                repository,
                previous_rows,
                window_days,
            )

    overview_delta = (
        _overview_delta(latest_ecosystem, previous_ecosystem, previous_complete_day)
        if previous_ecosystem is not None and previous_complete_day is not None
        else None
    )

    return {
        "schema_version": 1,
        "latest_complete_day": latest_day,
        "overview": _compact_scope(latest_ecosystem),
        "overview_delta": overview_delta,
        "latest_categories": latest_categories,
        "timeline": timeline,
        "comparison": {
            "window_start": window_start,
            "window_end": window_end,
            "window_days": window_days,
            "previous_window_start": previous_window_start,
            "previous_window_end": previous_window_end,
            "repositories": repositories,
        },
    }


def write_dashboard_payload(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the static OrbitFabric Analytics dashboard payload."
    )
    parser.add_argument("--rollups", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument(
        "--daily",
        type=Path,
        required=True,
        help="Normalized repository-day dataset used to build snapshot deltas.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/dashboard_data.json"),
    )
    args = parser.parse_args()

    payload = build_dashboard_payload(args.rollups, args.comparison, args.daily)
    write_dashboard_payload(payload, args.output)
    print(f"Wrote dashboard payload to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
