import tempfile
import unittest
from datetime import date
from pathlib import Path

from analytics.community_participation_public import (
    collect_public_participation,
    load_observation_start,
)


class FakeApi:
    def issues_updated_since(self, repository, start_date):
        return [
            {
                "created_at": "2026-08-20T08:00:00Z",
                "user": {"login": "alice"},
            },
            {
                "created_at": "2026-09-05T08:00:00Z",
                "user": {"login": "FAROTECH"},
            },
        ]

    def pull_requests_updated_since(self, repository, start_date):
        return [
            {
                "created_at": "2026-09-05T09:00:00Z",
                "user": {"login": "alice"},
            },
            {
                "created_at": "2026-09-06T09:00:00Z",
                "user": {"login": "bob"},
            },
        ]

    def issue_comments_since(self, repository, start_date):
        return [
            {
                "created_at": "2026-09-06T10:00:00Z",
                "user": {"login": "alice"},
            }
        ]


class PublicParticipationTests(unittest.TestCase):
    def test_observation_start_is_explicit_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.yml"
            path.write_text(
                """version: 1
history:
  lookback_days: 2
  observation_start_date: "2026-08-17"
""",
                encoding="utf-8",
            )
            self.assertEqual(load_observation_start(path), date(2026, 8, 17))

    def test_first_seen_is_reconstructed_without_persisted_actor_registry(self):
        repository = {
            "id": "core",
            "repo": "FAROTECH/orbitfabric",
            "category": "core",
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

        rows = collect_public_participation(
            [repository],
            2,
            date(2026, 8, 17),
            {"FAROTECH"},
            {"github-actions[bot]"},
            signals,
            FakeApi(),
            date(2026, 9, 6),
        )

        self.assertEqual([row["date"] for row in rows], ["2026-09-05", "2026-09-06"])

        sep5 = rows[0]
        self.assertEqual(sep5["participants_repo_count"], 2)
        self.assertEqual(sep5["other_participants_repo_count"], 1)
        # Alice was already observed on 2026-08-20, outside the 2-day output
        # window but inside the fixed observation baseline.
        self.assertEqual(sep5["participants_first_seen_repo_count"], 1)
        self.assertEqual(sep5["other_participants_first_seen_repo_count"], 0)

        sep6 = rows[1]
        self.assertEqual(sep6["participants_repo_count"], 2)
        self.assertEqual(sep6["other_participants_repo_count"], 2)
        self.assertEqual(sep6["participants_first_seen_repo_count"], 1)
        self.assertEqual(sep6["other_participants_first_seen_repo_count"], 1)


if __name__ == "__main__":
    unittest.main()
