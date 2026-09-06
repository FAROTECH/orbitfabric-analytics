#!/usr/bin/env python3
"""Collect repository-scoped issue and pull-request lifecycle events for M3d."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

FIELDNAMES = [
    "date",
    "repository_id",
    "repository",
    "category",
    "issues_opened",
    "issues_closed",
    "prs_opened",
    "prs_merged",
    "prs_closed_unmerged",
]

KNOWN_SIGNALS = {
    "issues_opened",
    "issues_closed",
    "prs_opened",
    "prs_merged",
    "prs_closed_unmerged",
}


class GitHubApi:
    def __init__(self, token: str | None = None) -> None:
        self.token = token.strip() if token else None

    def _headers(self, authenticated: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "orbitfabric-analytics",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if authenticated and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request_json(self, url: str) -> object:
        attempts = [True, False] if self.token else [False]
        last_error: HTTPError | None = None
        for authenticated in attempts:
            request = Request(url, headers=self._headers(authenticated))
            try:
                with urlopen(request, timeout=30) as response:
                    return json.load(response)
            except HTTPError as error:
                last_error = error
                if not authenticated or error.code not in {403, 404}:
                    raise
        assert last_error is not None
        raise last_error

    def issues_updated_since(self, repository: str, start_date: date) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        page = 1
        while True:
            query = urlencode(
                {
                    "state": "all",
                    "since": f"{start_date.isoformat()}T00:00:00Z",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                }
            )
            payload = self._request_json(
                f"https://api.github.com/repos/{repository}/issues?{query}"
            )
            if not isinstance(payload, list):
                raise ValueError(f"Unexpected issues response for {repository}")
            rows.extend(item for item in payload if isinstance(item, dict))
            if len(payload) < 100:
                break
            page += 1
        return rows

    def pull_requests_updated_since(
        self,
        repository: str,
        start_date: date,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        page = 1
        start_instant = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
        while True:
            query = urlencode(
                {
                    "state": "all",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                }
            )
            payload = self._request_json(
                f"https://api.github.com/repos/{repository}/pulls?{query}"
            )
            if not isinstance(payload, list):
                raise ValueError(f"Unexpected pull-request response for {repository}")

            items = [item for item in payload if isinstance(item, dict)]
            rows.extend(items)
            if len(payload) < 100:
                break

            last_updated = items[-1].get("updated_at") if items else None
            if isinstance(last_updated, str) and _parse_iso_datetime(last_updated) < start_instant:
                break
            page += 1
        return rows


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload


def load_policy(
    repository_config: Path,
    policy_config: Path,
) -> tuple[list[dict[str, object]], int, set[str]]:
    repositories_payload = _load_yaml(repository_config)
    policy = _load_yaml(policy_config)

    repositories = repositories_payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories.yml must define repositories")

    selection = policy.get("repository_selection")
    if not isinstance(selection, dict):
        raise ValueError("community-lifecycle.yml must define repository_selection")
    field = selection.get("field")
    expected = selection.get("value")
    if not isinstance(field, str):
        raise ValueError("repository_selection.field must be a string")

    history = policy.get("history")
    if not isinstance(history, dict) or not isinstance(history.get("lookback_days"), int):
        raise ValueError("history.lookback_days must be an integer")
    lookback_days = int(history["lookback_days"])
    if lookback_days < 1:
        raise ValueError("history.lookback_days must be >= 1")

    signals = policy.get("signals")
    if not isinstance(signals, dict):
        raise ValueError("community-lifecycle.yml must define signals")
    enabled_signals = {
        signal_id
        for signal_id, spec in signals.items()
        if isinstance(signal_id, str)
        and isinstance(spec, dict)
        and spec.get("collect") is True
    }
    unknown = enabled_signals - KNOWN_SIGNALS
    if unknown:
        raise ValueError(f"Unsupported lifecycle signals: {sorted(unknown)}")
    if not enabled_signals:
        raise ValueError("At least one lifecycle signal must be enabled")

    selected: list[dict[str, object]] = []
    for item in repositories:
        if not isinstance(item, dict) or item.get(field) != expected:
            continue
        for required in ("id", "repo", "category"):
            if not isinstance(item.get(required), str) or not item[required]:
                raise ValueError(f"Selected repository missing {required}: {item}")
        selected.append(item)

    if not selected:
        raise ValueError("Lifecycle repository selection is empty")

    return selected, lookback_days, enabled_signals


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _event_day(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return _parse_iso_datetime(value).date().isoformat()


def build_repository_rows(
    repository: dict[str, object],
    start_date: date,
    end_date: date,
    issues: list[dict[str, object]],
    pull_requests: list[dict[str, object]],
    enabled_signals: set[str],
) -> list[dict[str, object]]:
    days: list[str] = []
    cursor = start_date
    while cursor <= end_date:
        days.append(cursor.isoformat())
        cursor += timedelta(days=1)

    counters = {
        day: {signal: 0 for signal in KNOWN_SIGNALS}
        for day in days
    }

    for issue in issues:
        if "pull_request" in issue:
            continue
        created_day = _event_day(issue.get("created_at"))
        closed_day = _event_day(issue.get("closed_at"))
        if "issues_opened" in enabled_signals and created_day in counters:
            counters[created_day]["issues_opened"] += 1
        if "issues_closed" in enabled_signals and closed_day in counters:
            counters[closed_day]["issues_closed"] += 1

    for pull_request in pull_requests:
        created_day = _event_day(pull_request.get("created_at"))
        closed_day = _event_day(pull_request.get("closed_at"))
        merged_day = _event_day(pull_request.get("merged_at"))

        if "prs_opened" in enabled_signals and created_day in counters:
            counters[created_day]["prs_opened"] += 1
        if "prs_merged" in enabled_signals and merged_day in counters:
            counters[merged_day]["prs_merged"] += 1
        if (
            "prs_closed_unmerged" in enabled_signals
            and merged_day is None
            and closed_day in counters
        ):
            counters[closed_day]["prs_closed_unmerged"] += 1

    rows: list[dict[str, object]] = []
    for day in days:
        row: dict[str, object] = {
            "date": day,
            "repository_id": repository["id"],
            "repository": repository["repo"],
            "category": repository["category"],
        }
        for signal in KNOWN_SIGNALS:
            row[signal] = counters[day][signal] if signal in enabled_signals else ""
        rows.append(row)
    return rows


def collect_lifecycle(
    repositories: list[dict[str, object]],
    lookback_days: int,
    enabled_signals: set[str],
    api: GitHubApi,
    end_date: date,
) -> list[dict[str, object]]:
    start_date = end_date - timedelta(days=lookback_days - 1)
    rows: list[dict[str, object]] = []

    for repository in repositories:
        repo_name = str(repository["repo"])
        issues = api.issues_updated_since(repo_name, start_date)
        pull_requests = api.pull_requests_updated_since(repo_name, start_date)
        rows.extend(
            build_repository_rows(
                repository,
                start_date,
                end_date,
                issues,
                pull_requests,
                enabled_signals,
            )
        )

    return rows


def _read_existing(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDNAMES) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        return [dict(row) for row in reader]


def merge_and_write(path: Path, rows: list[dict[str, object]]) -> None:
    existing = _read_existing(path)
    replacement_keys = {(str(row["date"]), str(row["repository_id"])) for row in rows}
    merged: list[dict[str, object]] = [
        row
        for row in existing
        if (str(row["date"]), str(row["repository_id"])) not in replacement_keys
    ]
    merged.extend(rows)
    merged.sort(key=lambda row: (str(row["date"]), str(row["repository_id"])))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(merged)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect OrbitFabric issue / pull-request lifecycle signals."
    )
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="Inclusive UTC event date in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    end_date = date.fromisoformat(args.end_date)
    repositories, lookback_days, enabled_signals = load_policy(
        args.repositories,
        args.policy,
    )
    token = os.getenv("COMMUNITY_GITHUB_TOKEN") or os.getenv("GHRS_GITHUB_API_TOKEN")
    rows = collect_lifecycle(
        repositories,
        lookback_days,
        enabled_signals,
        GitHubApi(token),
        end_date,
    )
    merge_and_write(args.output, rows)
    print(
        f"Wrote {len(rows)} lifecycle repository-day rows through "
        f"{end_date.isoformat()} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
