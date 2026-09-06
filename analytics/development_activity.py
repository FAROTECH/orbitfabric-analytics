#!/usr/bin/env python3
"""Collect repository-scoped development activity context for M3c."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
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
    "default_branch",
    "commits_total",
    "first_party_commits",
    "automation_commits",
    "other_commits",
    "workflow_runs_total",
    "workflow_runs_success",
    "workflow_runs_failure",
    "workflow_runs_other",
]


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

    def repository(self, repository: str) -> dict[str, object]:
        payload = self._request_json(f"https://api.github.com/repos/{repository}")
        if not isinstance(payload, dict):
            raise ValueError(f"Unexpected repository response for {repository}")
        return payload

    def commits(
        self,
        repository: str,
        branch: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        page = 1
        params = {
            "sha": branch,
            "since": f"{start_date.isoformat()}T00:00:00Z",
            "until": f"{end_date.isoformat()}T23:59:59Z",
            "per_page": 100,
        }
        while True:
            query = dict(params)
            query["page"] = page
            payload = self._request_json(
                f"https://api.github.com/repos/{repository}/commits?{urlencode(query)}"
            )
            if not isinstance(payload, list):
                raise ValueError(f"Unexpected commits response for {repository}")
            rows.extend(item for item in payload if isinstance(item, dict))
            if len(payload) < 100:
                break
            page += 1
        return rows

    def workflow_runs(
        self,
        repository: str,
        branch: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        page = 1
        while True:
            query = urlencode(
                {
                    "branch": branch,
                    "created": f"{start_date.isoformat()}..{end_date.isoformat()}",
                    "per_page": 100,
                    "page": page,
                }
            )
            payload = self._request_json(
                f"https://api.github.com/repos/{repository}/actions/runs?{query}"
            )
            if not isinstance(payload, dict):
                raise ValueError(f"Unexpected workflow-runs response for {repository}")
            items = payload.get("workflow_runs")
            if not isinstance(items, list):
                raise ValueError(f"Missing workflow_runs list for {repository}")
            rows.extend(item for item in items if isinstance(item, dict))
            if len(items) < 100:
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
) -> tuple[list[dict[str, object]], int, set[str], set[str]]:
    repositories_payload = _load_yaml(repository_config)
    policy = _load_yaml(policy_config)

    repositories = repositories_payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories.yml must define repositories")

    selection = policy.get("repository_selection")
    if not isinstance(selection, dict):
        raise ValueError("development-activity.yml must define repository_selection")
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

    classification = policy.get("classification")
    if not isinstance(classification, dict):
        raise ValueError("classification must be a mapping")

    first_party = classification.get("first_party_logins")
    automation = classification.get("automation_logins")
    if not isinstance(first_party, list) or not all(isinstance(x, str) for x in first_party):
        raise ValueError("classification.first_party_logins must be a string list")
    if not isinstance(automation, list) or not all(isinstance(x, str) for x in automation):
        raise ValueError("classification.automation_logins must be a string list")

    selected: list[dict[str, object]] = []
    for item in repositories:
        if not isinstance(item, dict) or item.get(field) != expected:
            continue
        for required in ("id", "repo", "category"):
            if not isinstance(item.get(required), str) or not item[required]:
                raise ValueError(f"Selected repository missing {required}: {item}")
        selected.append(item)

    if not selected:
        raise ValueError("Development activity repository selection is empty")

    return selected, lookback_days, set(first_party), set(automation)


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _commit_day(commit: dict[str, object]) -> str:
    nested = commit.get("commit")
    if not isinstance(nested, dict):
        raise ValueError("Commit payload missing commit object")
    author = nested.get("author")
    committer = nested.get("committer")
    candidate = None
    if isinstance(author, dict):
        candidate = author.get("date")
    if not isinstance(candidate, str) and isinstance(committer, dict):
        candidate = committer.get("date")
    if not isinstance(candidate, str):
        raise ValueError("Commit payload missing timestamp")
    return _parse_iso_datetime(candidate).date().isoformat()


def _actor_logins(commit: dict[str, object]) -> set[str]:
    logins: set[str] = set()
    for field in ("author", "committer"):
        actor = commit.get(field)
        if isinstance(actor, dict) and isinstance(actor.get("login"), str):
            logins.add(str(actor["login"]))
    return logins


def _classify_commit(
    commit: dict[str, object],
    first_party: set[str],
    automation: set[str],
) -> str:
    logins = _actor_logins(commit)
    if logins & automation:
        return "automation"
    if logins & first_party:
        return "first_party"
    return "other"


def build_repository_rows(
    repository: dict[str, object],
    branch: str,
    start_date: date,
    end_date: date,
    commits: list[dict[str, object]],
    workflow_runs: list[dict[str, object]],
    first_party: set[str],
    automation: set[str],
) -> list[dict[str, object]]:
    days: list[str] = []
    cursor = start_date
    while cursor <= end_date:
        days.append(cursor.isoformat())
        cursor += timedelta(days=1)

    counters: dict[str, dict[str, int]] = {
        day: {
            "commits_total": 0,
            "first_party_commits": 0,
            "automation_commits": 0,
            "other_commits": 0,
            "workflow_runs_total": 0,
            "workflow_runs_success": 0,
            "workflow_runs_failure": 0,
            "workflow_runs_other": 0,
        }
        for day in days
    }

    for commit in commits:
        day = _commit_day(commit)
        if day not in counters:
            continue
        counters[day]["commits_total"] += 1
        kind = _classify_commit(commit, first_party, automation)
        counters[day][f"{kind}_commits"] += 1

    for run in workflow_runs:
        created_at = run.get("created_at")
        if not isinstance(created_at, str):
            continue
        day = _parse_iso_datetime(created_at).date().isoformat()
        if day not in counters:
            continue
        counters[day]["workflow_runs_total"] += 1
        conclusion = run.get("conclusion")
        if conclusion == "success":
            counters[day]["workflow_runs_success"] += 1
        elif conclusion == "failure":
            counters[day]["workflow_runs_failure"] += 1
        else:
            counters[day]["workflow_runs_other"] += 1

    rows: list[dict[str, object]] = []
    for day in days:
        row: dict[str, object] = {
            "date": day,
            "repository_id": repository["id"],
            "repository": repository["repo"],
            "category": repository["category"],
            "default_branch": branch,
        }
        row.update(counters[day])
        rows.append(row)
    return rows


def collect_activity(
    repositories: list[dict[str, object]],
    lookback_days: int,
    api: GitHubApi,
    end_date: date,
    first_party: set[str],
    automation: set[str],
) -> list[dict[str, object]]:
    start_date = end_date - timedelta(days=lookback_days - 1)
    rows: list[dict[str, object]] = []

    for repository in repositories:
        repo_name = str(repository["repo"])
        metadata = api.repository(repo_name)
        branch = metadata.get("default_branch")
        if not isinstance(branch, str) or not branch:
            raise ValueError(f"Repository {repo_name} has no default branch")
        commits = api.commits(repo_name, branch, start_date, end_date)
        workflow_runs = api.workflow_runs(repo_name, branch, start_date, end_date)
        rows.extend(
            build_repository_rows(
                repository,
                branch,
                start_date,
                end_date,
                commits,
                workflow_runs,
                first_party,
                automation,
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
        description="Collect OrbitFabric development activity context."
    )
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="Inclusive UTC activity date in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    end_date = date.fromisoformat(args.end_date)
    repositories, lookback_days, first_party, automation = load_policy(
        args.repositories,
        args.policy,
    )
    token = os.getenv("COMMUNITY_GITHUB_TOKEN") or os.getenv("GHRS_GITHUB_API_TOKEN")
    rows = collect_activity(
        repositories,
        lookback_days,
        GitHubApi(token),
        end_date,
        first_party,
        automation,
    )
    merge_and_write(args.output, rows)
    print(
        f"Wrote {len(rows)} development-activity repository-day rows through "
        f"{end_date.isoformat()} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
