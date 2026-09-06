import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from analytics.community_participation import (
    build_repository_rows,
    load_policy,
    load_registry,
    merge_and_write,
    write_registry,
)


class CommunityParticipationTests(unittest.TestCase):
    def test_policy_selects_official_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repositories = root / "repositories.yml"
            policy = root / "community-participation.yml"

            repositories.write_text(
                """version: 1
repositories:
  - id: core
    repo: FAROTECH/orbitfabric
    category: core
    include_in_rollups: true
  - id: adapter-template
    repo: FAROTECH/orbitfabric-adapter-template
    category: ecosystem
    include_in_rollups: false
""",
                encoding="utf-8",
            )
            policy.write_text(
                """version: 1
repository_selection:
  field: include_in_rollups
  value: true
history:
  lookback_days: 21
classification:
  first_party_logins: [FAROTECH]
  automation_logins: ["github-actions[bot]"]
signals:
  issue_author_events: {collect: true}
  pr_author_events: {collect: true}
  comment_events: {collect: true}
  participants_repo_count: {collect: true}
  first_party_participants_repo_count: {collect: true}
  automation_participants_repo_count: {collect: true}
  other_participants_repo_count: {collect: true}
  participants_first_seen_repo_count: {collect: true}
  other_participants_first_seen_repo_count: {collect: true}
""",
                encoding="utf-8",
            )

            selected, days, first_party, automation, signals = load_policy(
                repositories, policy
            )
            self.assertEqual([item["id"] for item in selected], ["core"])
            self.assertEqual(days, 21)
            self.assertEqual(first_party, {"FAROTECH"})
            self.assertEqual(automation, {"github-actions[bot]"})
            self.assertIn("participants_repo_count", signals)

    def test_daily_participants_are_repo_scoped_and_first_seen_is_baseline_relative(self) -> None:
        repository = {
            "id": "core",
            "repo": "FAROTECH/orbitfabric",
            "category": "core",
        }
        issues = [
            {
                "created_at": "2026-09-05T08:00:00Z",
                "user": {"login": "FAROTECH"},
            },
            {
                "created_at": "2026-09-05T09:00:00Z",
                "user": {"login": "alice"},
            },
            {
                "created_at": "2026-09-05T10:00:00Z",
                "user": {"login": "ignored-pr-marker"},
                "pull_request": {"url": "https://api.github.com/example"},
            },
        ]
        pull_requests = [
            {
                "created_at": "2026-09-05T11:00:00Z",
                "user": {"login": "FAROTECH"},
            },
            {
                "created_at": "2026-09-06T11:00:00Z",
                "user": {"login": "bob"},
            },
        ]
        comments = [
            {
                "created_at": "2026-09-05T12:00:00Z",
                "user": {"login": "alice"},
            },
            {
                "created_at": "2026-09-05T13:00:00Z",
                "user": {"login": "github-actions[bot]"},
            },
            {
                "created_at": "2026-09-06T12:00:00Z",
                "user": {"login": "alice"},
            },
        ]
        registry = {
            "schema_version": 1,
            "observation_start_date": "2026-09-05",
            "repositories": {},
        }
        signals = {
            "issue_author_events",
            "pr_author_events",
            "comment_events",
            "participants_repo_count",
            "first_party_participants_repo_count",
            "automation_participants_repo_count",
            "other_participants_repo_count",
            "participants_first_seen_repo_count",
            "other_participants_first_seen_repo_count",
        }

        rows = build_repository_rows(
            repository,
            date(2026, 9, 5),
            date(2026, 9, 6),
            issues,
            pull_requests,
            comments,
            {"FAROTECH"},
            {"github-actions[bot]"},
            signals,
            registry,
        )

        first = rows[0]
        self.assertEqual(first["issue_author_events"], 2)
        self.assertEqual(first["pr_author_events"], 1)
        self.assertEqual(first["comment_events"], 2)
        self.assertEqual(first["participants_repo_count"], 3)
        self.assertEqual(first["first_party_participants_repo_count"], 1)
        self.assertEqual(first["automation_participants_repo_count"], 1)
        self.assertEqual(first["other_participants_repo_count"], 1)
        self.assertEqual(first["participants_first_seen_repo_count"], 3)
        self.assertEqual(first["other_participants_first_seen_repo_count"], 1)

        second = rows[1]
        self.assertEqual(second["pr_author_events"], 1)
        self.assertEqual(second["comment_events"], 1)
        self.assertEqual(second["participants_repo_count"], 2)
        self.assertEqual(second["other_participants_repo_count"], 2)
        self.assertEqual(second["participants_first_seen_repo_count"], 1)
        self.assertEqual(second["other_participants_first_seen_repo_count"], 1)

        actors = registry["repositories"]["core"]["actors"]
        self.assertEqual(actors["alice"]["first_observed_date"], "2026-09-05")
        self.assertEqual(actors["bob"]["first_observed_date"], "2026-09-06")
        self.assertEqual(actors["FAROTECH"]["classification"], "first_party")

    def test_registry_preserves_earlier_first_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "participants.json"
            payload = {
                "schema_version": 1,
                "observation_start_date": "2026-09-05",
                "repositories": {
                    "core": {
                        "repository": "FAROTECH/orbitfabric",
                        "actors": {
                            "alice": {
                                "first_observed_date": "2026-09-05",
                                "classification": "other",
                            }
                        },
                    }
                },
            }
            write_registry(path, payload)
            loaded = load_registry(path)
            self.assertEqual(loaded, payload)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["schema_version"], 1
            )

    def test_history_merge_replaces_recollected_repository_days(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "community_participation_daily.csv"
            base = {
                "date": "2026-09-05",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "issue_author_events": 1,
                "pr_author_events": 0,
                "comment_events": 1,
                "participants_repo_count": 1,
                "first_party_participants_repo_count": 1,
                "automation_participants_repo_count": 0,
                "other_participants_repo_count": 0,
                "participants_first_seen_repo_count": 1,
                "other_participants_first_seen_repo_count": 0,
            }
            merge_and_write(output, [base])
            replacement = dict(base)
            replacement["comment_events"] = 2
            merge_and_write(output, [replacement])

            text = output.read_text(encoding="utf-8")
            self.assertEqual(text.count("2026-09-05"), 1)
            self.assertIn(",1,0,2,1,1,0,0,1,0", text)


if __name__ == "__main__":
    unittest.main()
