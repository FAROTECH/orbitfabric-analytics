#!/usr/bin/env python3
"""Collect repository-scoped participation without persisting raw actor identities.

The public collector reconstructs repository-scoped first-observed semantics from a
fixed observation baseline on every run. Raw GitHub logins live only in memory for
the duration of the job and are never written to retained analytics state.
"""

from __future__ import annotations

import argparse
import os
from datetime import date, timedelta
from pathlib import Path

import yaml

try:
    from analytics.community_participation import (
        GitHubApi,
        _empty_registry,
        build_repository_rows,
        load_policy,
        merge_and_write,
    )
except ModuleNotFoundError:
    # Direct script execution, e.g. `python app/analytics/community_participation_public.py`.
    from community_participation import (  # type: ignore
        GitHubApi,
        _empty_registry,
        build_repository_rows,
        load_policy,
        merge_and_write,
    )


def load_observation_start(policy_path: Path) -> date:
    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{policy_path} must contain a YAML mapping")
    history = payload.get("history")
    if not isinstance(history, dict):
        raise ValueError("community-participation.yml must define history")
    value = history.get("observation_start_date")
    if not isinstance(value, str) or not value:
        raise ValueError("history.observation_start_date must be YYYY-MM-DD")
    return date.fromisoformat(value)


def collect_public_participation(
    repositories: list[dict[str, object]],
    lookback_days: int,
    observation_start: date,
    first_party: set[str],
    automation: set[str],
    enabled_signals: set[str],
    api: GitHubApi,
    end_date: date,
) -> list[dict[str, object]]:
    output_start = end_date - timedelta(days=lookback_days - 1)
    if observation_start > output_start:
        observation_start = output_start

    rows: list[dict[str, object]] = []
    for repository in repositories:
        repo_name = str(repository["repo"])
        issues = api.issues_updated_since(repo_name, observation_start)
        pull_requests = api.pull_requests_updated_since(repo_name, observation_start)
        comments = api.issue_comments_since(repo_name, observation_start)

        # Reconstruct first-observed state from the fixed public observation
        # baseline. The registry exists only in process memory and is discarded.
        registry = _empty_registry()
        registry["observation_start_date"] = observation_start.isoformat()
        build_repository_rows(
            repository,
            observation_start,
            end_date,
            issues,
            pull_requests,
            comments,
            first_party,
            automation,
            enabled_signals,
            registry,
        )

        rows.extend(
            build_repository_rows(
                repository,
                output_start,
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect public-safe OrbitFabric participation signals."
    )
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
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
    observation_start = load_observation_start(args.policy)
    token = os.getenv("COMMUNITY_GITHUB_TOKEN") or os.getenv("GHRS_GITHUB_API_TOKEN")
    rows = collect_public_participation(
        repositories,
        lookback_days,
        observation_start,
        first_party,
        automation,
        enabled_signals,
        GitHubApi(token),
        end_date,
    )
    merge_and_write(args.output, rows)
    print(
        f"Wrote {len(rows)} public-safe participation repository-day rows through "
        f"{end_date.isoformat()} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
