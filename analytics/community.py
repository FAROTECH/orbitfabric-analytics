#!/usr/bin/env python3
"""Collect and retain repository-scoped GitHub community stock signals."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date
from pathlib import Path
from typing import Callable, Iterable
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

FIELDNAMES = [
    "date",
    "repository_id",
    "repository",
    "category",
    "stars_total",
    "forks_total",
    "open_issues_total",
    "open_pull_requests_total",
    "contributors_repo_count",
]

KNOWN_SIGNALS = {
    "stars_total",
    "forks_total",
    "open_issues_total",
    "open_pull_requests_total",
    "contributors_repo_count",
}


class GitHubApi:
    """Small REST client for public repository community snapshots.

    The configured token is used when available. If a fine-grained token lacks
    permission for a public endpoint, 403/404 responses are retried without
    authentication so M3a can still consume public GitHub evidence.
    """

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

    def _collection(
        self,
        repository: str,
        endpoint: str,
        *,
        query: str = "",
    ) -> Iterable[dict[str, object]]:
        page = 1
        while True:
            separator = "&" if query else "?"
            suffix = f"{query}{separator}per_page=100&page={page}"
            url = f"https://api.github.com/repos/{repository}/{endpoint}{suffix}"
            payload = self._request_json(url)
            if not isinstance(payload, list):
                raise ValueError(
                    f"Unexpected {endpoint} response for {repository}: expected list"
                )
            for item in payload:
                if isinstance(item, dict):
                    yield item
            if len(payload) < 100:
                break
            page += 1

    def open_issue_count(self, repository: str) -> int:
        return sum(
            1
            for item in self._collection(repository, "issues", query="?state=open")
            if "pull_request" not in item
        )

    def open_pull_request_count(self, repository: str) -> int:
        return sum(
            1
            for _ in self._collection(repository, "pulls", query="?state=open")
        )

    def contributor_count(self, repository: str) -> int:
        return sum(
            1
            for _ in self._collection(repository, "contributors", query="?anon=1")
        )


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload


def load_selected_repositories(
    repository_config: Path,
    policy_config: Path,
) -> tuple[list[dict[str, object]], set[str]]:
    repositories_payload = _load_yaml(repository_config)
    policy_payload = _load_yaml(policy_config)

    repositories = repositories_payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories.yml must define a repositories list")

    selection = policy_payload.get("repository_selection")
    if not isinstance(selection, dict):
        raise ValueError("community-signals.yml must define repository_selection")
    field = selection.get("field")
    expected = selection.get("value")
    if not isinstance(field, str):
        raise ValueError("repository_selection.field must be a string")

    signals = policy_payload.get("signals")
    if not isinstance(signals, dict):
        raise ValueError("community-signals.yml must define signals")

    enabled_signals = {
        signal_id
        for signal_id, spec in signals.items()
        if isinstance(signal_id, str)
        and isinstance(spec, dict)
        and spec.get("collect") is True
    }
    unknown = enabled_signals - KNOWN_SIGNALS
    if unknown:
        raise ValueError(f"Unsupported community signals: {sorted(unknown)}")
    if not enabled_signals:
        raise ValueError("At least one community signal must be enabled")

    selected: list[dict[str, object]] = []
    for item in repositories:
        if not isinstance(item, dict):
            continue
        if item.get(field) != expected:
            continue
        for required in ("id", "repo", "category"):
            if not isinstance(item.get(required), str) or not item[required]:
                raise ValueError(f"Selected repository is missing {required}: {item}")
        selected.append(item)

    if not selected:
        raise ValueError("Community repository selection is empty")
    return selected, enabled_signals


def collect_snapshot(
    repositories: list[dict[str, object]],
    enabled_signals: set[str],
    api: GitHubApi,
    snapshot_date: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for repository in repositories:
        repo_name = str(repository["repo"])
        metadata = api.repository(repo_name)

        row: dict[str, object] = {
            "date": snapshot_date,
            "repository_id": repository["id"],
            "repository": repo_name,
            "category": repository["category"],
            "stars_total": "",
            "forks_total": "",
            "open_issues_total": "",
            "open_pull_requests_total": "",
            "contributors_repo_count": "",
        }

        if "stars_total" in enabled_signals:
            row["stars_total"] = int(metadata.get("stargazers_count", 0))
        if "forks_total" in enabled_signals:
            row["forks_total"] = int(metadata.get("forks_count", 0))
        if "open_issues_total" in enabled_signals:
            row["open_issues_total"] = api.open_issue_count(repo_name)
        if "open_pull_requests_total" in enabled_signals:
            row["open_pull_requests_total"] = api.open_pull_request_count(repo_name)
        if "contributors_repo_count" in enabled_signals:
            row["contributors_repo_count"] = api.contributor_count(repo_name)

        rows.append(row)
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


def merge_and_write(
    output_path: Path,
    snapshot_rows: list[dict[str, object]],
) -> None:
    existing = _read_existing(output_path)
    replacement_keys = {
        (str(row["date"]), str(row["repository_id"])) for row in snapshot_rows
    }
    merged: list[dict[str, object]] = [
        row
        for row in existing
        if (str(row["date"]), str(row["repository_id"])) not in replacement_keys
    ]
    merged.extend(snapshot_rows)
    merged.sort(key=lambda row: (str(row["date"]), str(row["repository_id"])))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(merged)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect GitHub community stock signals for OrbitFabric repositories."
    )
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Snapshot date in YYYY-MM-DD format. Defaults to the runner date.",
    )
    args = parser.parse_args()

    date.fromisoformat(args.date)
    repositories, enabled_signals = load_selected_repositories(
        args.repositories,
        args.policy,
    )

    token = os.getenv("COMMUNITY_GITHUB_TOKEN") or os.getenv("GHRS_GITHUB_API_TOKEN")
    rows = collect_snapshot(
        repositories,
        enabled_signals,
        GitHubApi(token),
        args.date,
    )
    merge_and_write(args.output, rows)
    print(
        f"Wrote {len(rows)} community repository snapshots for {args.date} "
        f"to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
