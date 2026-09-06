#!/usr/bin/env python3
"""Project M3 community and engineering evidence into dashboard_data.json."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

STOCK_VALUE_FIELDS = [
    "stars_total",
    "forks_total",
    "open_issues_total",
    "open_pull_requests_total",
    "contributors_repo_count",
]

DEVELOPMENT_FIELDS = [
    "commits_total",
    "first_party_commits",
    "automation_commits",
    "other_commits",
    "workflow_runs_total",
    "workflow_runs_success",
    "workflow_runs_failure",
    "workflow_runs_other",
]

LIFECYCLE_FIELDS = [
    "issues_opened",
    "issues_closed",
    "prs_opened",
    "prs_merged",
    "prs_closed_unmerged",
]

PARTICIPATION_FIELDS = [
    "issue_author_events",
    "pr_author_events",
    "comment_events",
    "participants_repo_count",
    "first_party_participants_repo_count",
    "automation_participants_repo_count",
    "other_participants_repo_count",
    "participants_first_seen_repo_count",
    "other_participants_first_seen_repo_count",
]


def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
        return [dict(row) for row in reader]


def _int(row: dict[str, str], field: str) -> int:
    value = row.get(field, "").strip()
    return 0 if value == "" else int(value)


def _optional_int(row: dict[str, str], field: str) -> int | None:
    value = row.get(field, "").strip()
    return None if value == "" else int(value)


def _aggregate_rows(
    rows: list[dict[str, str]],
    fields: list[str],
    repository_ids: list[str],
    window_start: str,
    window_end: str,
) -> tuple[dict[str, object], dict[str, dict[str, int]]]:
    start = date.fromisoformat(window_start)
    end = date.fromisoformat(window_end)
    expected_days = (end - start).days + 1
    expected_rows = expected_days * len(repository_ids)

    filtered = [
        row
        for row in rows
        if row.get("repository_id") in repository_ids
        and start <= date.fromisoformat(row["date"]) <= end
    ]

    seen = {(row["date"], row["repository_id"]) for row in filtered}
    if len(seen) != len(filtered):
        raise ValueError("Duplicate repository-day rows in dashboard ecosystem context input")

    totals = {field: sum(_int(row, field) for row in filtered) for field in fields}
    totals.update(
        {
            "rows_expected": expected_rows,
            "rows_available": len(filtered),
            "coverage_pct": round(100.0 * len(filtered) / expected_rows, 2)
            if expected_rows
            else 100.0,
            "coverage_complete": len(filtered) == expected_rows,
        }
    )

    by_repository: dict[str, dict[str, int]] = {
        repository_id: {field: 0 for field in fields}
        for repository_id in repository_ids
    }
    for row in filtered:
        target = by_repository[row["repository_id"]]
        for field in fields:
            target[field] += _int(row, field)

    return totals, by_repository


def _stock_context(
    rows: list[dict[str, str]],
    repository_ids: list[str],
) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    selected = [row for row in rows if row.get("repository_id") in repository_ids]
    if len(selected) != len(repository_ids):
        raise ValueError("Community stock comparison does not cover every dashboard repository")

    current_dates = {row["current_date"] for row in selected}
    previous_dates = {row["previous_date"] for row in selected}
    gaps = {row["snapshot_gap_days"] for row in selected}
    if len(current_dates) != 1 or len(previous_dates) != 1 or len(gaps) != 1:
        raise ValueError("Community stock rows do not share one snapshot boundary")

    comparable = all(row["comparable"].strip().lower() == "true" for row in selected)
    totals: dict[str, object] = {}
    for field in STOCK_VALUE_FIELDS:
        totals[field] = sum(_int(row, field) for row in selected)
        delta_field = f"{field}_delta"
        delta_values = [_optional_int(row, delta_field) for row in selected]
        totals[delta_field] = (
            sum(value for value in delta_values if value is not None)
            if comparable and all(value is not None for value in delta_values)
            else None
        )

    by_repository: dict[str, dict[str, object]] = {}
    for row in selected:
        repository_id = row["repository_id"]
        item: dict[str, object] = {
            "repository_id": repository_id,
            "repository": row["repository"],
            "category": row["category"],
        }
        for field in STOCK_VALUE_FIELDS:
            item[field] = _int(row, field)
            item[f"{field}_delta"] = _optional_int(row, f"{field}_delta")
        by_repository[repository_id] = item

    return (
        {
            "current_date": next(iter(current_dates)),
            "previous_date": next(iter(previous_dates)),
            "snapshot_gap_days": int(next(iter(gaps))),
            "comparable": comparable,
            "totals": totals,
            "repositories": [by_repository[repository_id] for repository_id in repository_ids],
        },
        by_repository,
    )


def project_ecosystem_context(
    dashboard: dict[str, object],
    community_rows: list[dict[str, str]],
    development_rows: list[dict[str, str]],
    lifecycle_rows: list[dict[str, str]],
    participation_rows: list[dict[str, str]],
) -> dict[str, object]:
    if int(dashboard.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported dashboard schema")

    comparison = dashboard.get("comparison")
    if not isinstance(comparison, dict):
        raise ValueError("Dashboard comparison section is required")
    repositories = comparison.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("Dashboard repository comparison is empty")

    repository_ids = [str(item["repository_id"]) for item in repositories]
    window_start = str(comparison["window_start"])
    window_end = str(comparison["window_end"])
    window_days = int(comparison["window_days"])

    stock, stock_by_repository = _stock_context(community_rows, repository_ids)
    development, development_by_repository = _aggregate_rows(
        development_rows,
        DEVELOPMENT_FIELDS,
        repository_ids,
        window_start,
        window_end,
    )
    lifecycle, lifecycle_by_repository = _aggregate_rows(
        lifecycle_rows,
        LIFECYCLE_FIELDS,
        repository_ids,
        window_start,
        window_end,
    )
    participation, participation_by_repository = _aggregate_rows(
        participation_rows,
        PARTICIPATION_FIELDS,
        repository_ids,
        window_start,
        window_end,
    )

    repository_context: list[dict[str, object]] = []
    for repository in repositories:
        repository_id = str(repository["repository_id"])
        repository_context.append(
            {
                "repository_id": repository_id,
                "repository": repository["repository"],
                "category": repository["category"],
                "stock": stock_by_repository[repository_id],
                "development": development_by_repository[repository_id],
                "lifecycle": lifecycle_by_repository[repository_id],
                "participation": participation_by_repository[repository_id],
            }
        )

    dashboard["ecosystem_context"] = {
        "stock": stock,
        "aligned_window": {
            "window_start": window_start,
            "window_end": window_end,
            "window_days": window_days,
            "development": development,
            "lifecycle": lifecycle,
            "participation": participation,
            "repositories": repository_context,
        },
        "semantics": {
            "stock_snapshot_may_be_newer_than_traffic": True,
            "participants_are_repository_scoped": True,
            "participant_totals_are_repo_day_sums": True,
            "other_participant_does_not_mean_external_user": True,
            "development_activity_is_context_not_attribution": True,
        },
    }
    return dashboard


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project M3 ecosystem context into dashboard_data.json."
    )
    parser.add_argument("--dashboard", type=Path, required=True)
    parser.add_argument("--community", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--lifecycle", type=Path, required=True)
    parser.add_argument("--participation", type=Path, required=True)
    args = parser.parse_args()

    dashboard = json.loads(args.dashboard.read_text(encoding="utf-8"))
    community_rows = _read_csv(
        args.community,
        {
            "repository_id",
            "repository",
            "category",
            "current_date",
            "previous_date",
            "snapshot_gap_days",
            "comparable",
            *STOCK_VALUE_FIELDS,
            *(f"{field}_delta" for field in STOCK_VALUE_FIELDS),
        },
    )
    development_rows = _read_csv(
        args.development,
        {"date", "repository_id", *DEVELOPMENT_FIELDS},
    )
    lifecycle_rows = _read_csv(
        args.lifecycle,
        {"date", "repository_id", *LIFECYCLE_FIELDS},
    )
    participation_rows = _read_csv(
        args.participation,
        {"date", "repository_id", *PARTICIPATION_FIELDS},
    )

    payload = project_ecosystem_context(
        dashboard,
        community_rows,
        development_rows,
        lifecycle_rows,
        participation_rows,
    )
    args.dashboard.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Projected M3 ecosystem context into {args.dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
