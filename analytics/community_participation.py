#!/usr/bin/env python3
"""Collect repository-scoped GitHub participation signals for M3e."""

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

KNOWN_SIGNALS = set(FIELDNAMES[4:])


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

    def issue_comments_since(
        self,
        repository: str,
        start_date: date,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        page = 1
        while True:
            query = urlencode(
                {
                    "since": f"{start_date.isoformat()}T00:00:00Z",
                    "sort": "created",
                    "direction": "asc",
                    "per_page": 100,
                    "page": page,
                }
            )
            payload = self._request_json(
                f"https://api.github.com/repos/{repository}/issues/comments?{query}"
            )
            if not isinstance(payload, list):
                raise ValueError(f"Unexpected issue-comments response for {repository}")
            rows.extend(item for item in payload if isinstance(item, dict))
            if len(payload) < 100:
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
) -> tuple[list[dict[str, object]], int, set[str], set[str], set[str]]:
    repositories_payload = _load_yaml(repository_config)
    policy = _load_yaml(policy_config)

    repositories = repositories_payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories.yml must define repositories")

    selection = policy.get("repository_selection")
    if not isinstance(selection, dict):
        raise ValueError("community-participation.yml must define repository_selection")
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

    signals = policy.get("signals")
    if not isinstance(signals, dict):
        raise ValueError("community-participation.yml must define signals")
    enabled_signals = {
        signal_id
        for signal_id, spec in signals.items()
        if isinstance(signal_id, str)
        and isinstance(spec, dict)
        and spec.get("collect") is True
    }
    unknown = enabled_signals - KNOWN_SIGNALS
    if unknown:
        raise ValueError(f"Unsupported participation signals: {sorted(unknown)}")
    if not enabled_signals:
        raise ValueError("At least one participation signal must be enabled")

    selected: list[dict[str, object]] = []
    for item in repositories:
        if not isinstance(item, dict) or item.get(field) != expected:
            continue
        for required in ("id", "repo", "category"):
            if not isinstance(item.get(required), str) or not item[required]:
                raise ValueError(f"Selected repository missing {required}: {item}")
        selected.append(item)

    if not selected:
        raise ValueError("Participation repository selection is empty")

    return selected, lookback_days, set(first_party), set(automation), enabled_signals


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _event_day(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return _parse_iso_datetime(value).date().isoformat()


def _actor_login(item: dict[str, object]) -> str | None:
    user = item.get("user")
    if not isinstance(user, dict):
        return None
    login = user.get("login")
    if not isinstance(login, str) or not login.strip():
        return None
    return login.strip()


def _classification(login: str, first_party: set[str], automation: set[str]) -> str:
    if login in automation:
        return "automation"
    if login in first_party:
        return "first_party"
    return "other"


def _empty_registry() -> dict[str, object]:
    return {
        "schema_version": 1,
        "observation_start_date": None,
        "repositories": {},
    }


def load_registry(path: Path) -> dict[str, object]:
    if not path.exists():
        return _empty_registry()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError(f"Unsupported participant registry schema in {path}")
    repositories = payload.get("repositories")
    if not isinstance(repositories, dict):
        raise ValueError(f"Participant registry repositories must be a mapping in {path}")
    return payload


def _record_actor(
    registry: dict[str, object],
    repository: dict[str, object],
    login: str,
    observed_day: str,
    actor_classification: str,
) -> None:
    repositories = registry.setdefault("repositories", {})
    if not isinstance(repositories, dict):
        raise ValueError("Participant registry repositories must be a mapping")
    repository_id = str(repository["id"])
    repo_entry = repositories.setdefault(
        repository_id,
        {
            "repository": str(repository["repo"]),
            "actors": {},
        },
    )
    if not isinstance(repo_entry, dict):
        raise ValueError(f"Invalid registry repository entry: {repository_id}")
    repo_entry["repository"] = str(repository["repo"])
    actors = repo_entry.setdefault("actors", {})
    if not isinstance(actors, dict):
        raise ValueError(f"Invalid actor registry for {repository_id}")

    existing = actors.get(login)
    if not isinstance(existing, dict):
        actors[login] = {
            "first_observed_date": observed_day,
            "classification": actor_classification,
        }
        return

    previous = existing.get("first_observed_date")
    if not isinstance(previous, str) or observed_day < previous:
        existing["first_observed_date"] = observed_day
    existing["classification"] = actor_classification


def _first_observed_date(
    registry: dict[str, object],
    repository_id: str,
    login: str,
) -> str | None:
    repositories = registry.get("repositories")
    if not isinstance(repositories, dict):
        return None
    repository = repositories.get(repository_id)
    if not isinstance(repository, dict):
        return None
    actors = repository.get("actors")
    if not isinstance(actors, dict):
        return None
    actor = actors.get(login)
    if not isinstance(actor, dict):
        return None
    value = actor.get("first_observed_date")
    return value if isinstance(value, str) else None


def build_repository_rows(
    repository: dict[str, object],
    start_date: date,
    end_date: date,
    issues: list[dict[str, object]],
    pull_requests: list[dict[str, object]],
    comments: list[dict[str, object]],
    first_party: set[str],
    automation: set[str],
    enabled_signals: set[str],
    registry: dict[str, object],
) -> list[dict[str, object]]:
    days: list[str] = []
    cursor = start_date
    while cursor <= end_date:
        days.append(cursor.isoformat())
        cursor += timedelta(days=1)

    event_counts: dict[str, dict[str, int]] = {
        day: {
            "issue_author_events": 0,
            "pr_author_events": 0,
            "comment_events": 0,
        }
        for day in days
    }
    actors_by_day: dict[str, set[str]] = defaultdict(set)

    def observe(item: dict[str, object], timestamp_field: str, event_signal: str) -> None:
        day = _event_day(item.get(timestamp_field))
        if day not in event_counts:
            return
        if event_signal in enabled_signals:
            event_counts[day][event_signal] += 1
        login = _actor_login(item)
        if login is None:
            return
        actors_by_day[day].add(login)
        _record_actor(
            registry,
            repository,
            login,
            day,
            _classification(login, first_party, automation),
        )

    for issue in issues:
        if "pull_request" in issue:
            continue
        observe(issue, "created_at", "issue_author_events")

    for pull_request in pull_requests:
        observe(pull_request, "created_at", "pr_author_events")

    for comment in comments:
        observe(comment, "created_at", "comment_events")

    repository_id = str(repository["id"])
    rows: list[dict[str, object]] = []
    for day in days:
        actors = actors_by_day.get(day, set())
        first_party_actors = {login for login in actors if login in first_party}
        automation_actors = {login for login in actors if login in automation}
        other_actors = actors - first_party_actors - automation_actors
        first_seen = {
            login
            for login in actors
            if _first_observed_date(registry, repository_id, login) == day
        }
        other_first_seen = first_seen & other_actors

        values: dict[str, object] = {
            "date": day,
            "repository_id": repository["id"],
            "repository": repository["repo"],
            "category": repository["category"],
            **event_counts[day],
            "participants_repo_count": len(actors),
            "first_party_participants_repo_count": len(first_party_actors),
            "automation_participants_repo_count": len(automation_actors),
            "other_participants_repo_count": len(other_actors),
            "participants_first_seen_repo_count": len(first_seen),
            "other_participants_first_seen_repo_count": len(other_first_seen),
        }
        for signal in KNOWN_SIGNALS:
            if signal not in enabled_signals:
                values[signal] = ""
        rows.append(values)
    return rows


def collect_participation(
    repositories: list[dict[str, object]],
    lookback_days: int,
    first_party: set[str],
    automation: set[str],
    enabled_signals: set[str],
    api: GitHubApi,
    end_date: date,
    registry: dict[str, object],
) -> list[dict[str, object]]:
    start_date = end_date - timedelta(days=lookback_days - 1)
    current_start = registry.get("observation_start_date")
    if not isinstance(current_start, str) or start_date.isoformat() < current_start:
        registry["observation_start_date"] = start_date.isoformat()

    rows: list[dict[str, object]] = []
    for repository in repositories:
        repo_name = str(repository["repo"])
        issues = api.issues_updated_since(repo_name, start_date)
        pull_requests = api.pull_requests_updated_since(repo_name, start_date)
        comments = api.issue_comments_since(repo_name, start_date)
        rows.extend(
            build_repository_rows(
                repository,
                start_date,
                end_date,
                issues,
                pull_requests,
                comments,
                first_party,
                automation,
                enabled_signals,
                registry,
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


def write_registry(path: Path, registry: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect OrbitFabric repository-scoped participation signals."
    )
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="Inclusive UTC participation date in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    end_date = date.fromisoformat(args.end_date)
    repositories, lookback_days, first_party, automation, enabled_signals = load_policy(
        args.repositories,
        args.policy,
    )
    registry = load_registry(args.registry)
    token = os.getenv("COMMUNITY_GITHUB_TOKEN") or os.getenv("GHRS_GITHUB_API_TOKEN")
    rows = collect_participation(
        repositories,
        lookback_days,
        first_party,
        automation,
        enabled_signals,
        GitHubApi(token),
        end_date,
        registry,
    )
    merge_and_write(args.output, rows)
    write_registry(args.registry, registry)
    print(
        f"Wrote {len(rows)} participation repository-day rows through "
        f"{end_date.isoformat()} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
