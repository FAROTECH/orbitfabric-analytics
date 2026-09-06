import tempfile
import unittest
from datetime import date
from pathlib import Path

from analytics.community_lifecycle import (
    build_repository_rows,
    load_policy,
    merge_and_write,
)


class CommunityLifecycleTests(unittest.TestCase):
    def test_policy_selects_official_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repositories = root / "repositories.yml"
            policy = root / "community-lifecycle.yml"

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
signals:
  issues_opened: {collect: true}
  issues_closed: {collect: true}
  prs_opened: {collect: true}
  prs_merged: {collect: true}
  prs_closed_unmerged: {collect: true}
""",
                encoding="utf-8",
            )

            selected, days, signals = load_policy(repositories, policy)
            self.assertEqual([item["id"] for item in selected], ["core"])
            self.assertEqual(days, 21)
            self.assertEqual(
                signals,
                {
                    "issues_opened",
                    "issues_closed",
                    "prs_opened",
                    "prs_merged",
                    "prs_closed_unmerged",
                },
            )

    def test_build_rows_counts_lifecycle_events_without_stock_inference(self) -> None:
        repository = {
            "id": "core",
            "repo": "FAROTECH/orbitfabric",
            "category": "core",
        }
        issues = [
            {"number": 1, "created_at": "2026-09-05T08:00:00Z"},
            {"number": 2, "created_at": "2026-09-05T09:00:00Z"},
            {"number": 3, "created_at": "2026-09-05T10:00:00Z"},
            {
                "number": 10,
                "created_at": "2026-09-05T11:00:00Z",
                "pull_request": {"url": "https://api.github.com/example"},
            },
        ]
        pull_requests = [
            {"number": 10, "created_at": "2026-09-05T08:30:00Z"},
            {"number": 11, "created_at": "2026-09-05T13:00:00Z"},
            {"number": 12, "created_at": "2026-09-06T14:00:00Z"},
        ]
        lifecycle_events = [
            {
                "event": "closed",
                "created_at": "2026-09-05T12:00:00Z",
                "issue": {"number": 1},
            },
            {
                "event": "closed",
                "created_at": "2026-09-06T10:00:00Z",
                "issue": {"number": 3},
            },
            {
                "event": "merged",
                "created_at": "2026-09-05T09:30:00Z",
                "issue": {
                    "number": 10,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
            {
                "event": "closed",
                "created_at": "2026-09-05T09:30:01Z",
                "issue": {
                    "number": 10,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
            {
                "event": "closed",
                "created_at": "2026-09-06T08:00:00Z",
                "issue": {
                    "number": 11,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
        ]

        rows = build_repository_rows(
            repository,
            date(2026, 9, 5),
            date(2026, 9, 6),
            issues,
            pull_requests,
            lifecycle_events,
            {
                "issues_opened",
                "issues_closed",
                "prs_opened",
                "prs_merged",
                "prs_closed_unmerged",
            },
        )

        first = rows[0]
        self.assertEqual(first["issues_opened"], 3)
        self.assertEqual(first["issues_closed"], 1)
        self.assertEqual(first["prs_opened"], 2)
        self.assertEqual(first["prs_merged"], 1)
        self.assertEqual(first["prs_closed_unmerged"], 0)

        second = rows[1]
        self.assertEqual(second["issues_opened"], 0)
        self.assertEqual(second["issues_closed"], 1)
        self.assertEqual(second["prs_opened"], 1)
        self.assertEqual(second["prs_merged"], 0)
        self.assertEqual(second["prs_closed_unmerged"], 1)

    def test_close_before_later_merge_remains_closed_unmerged_event(self) -> None:
        repository = {
            "id": "core",
            "repo": "FAROTECH/orbitfabric",
            "category": "core",
        }
        lifecycle_events = [
            {
                "event": "closed",
                "created_at": "2026-09-05T10:00:00Z",
                "issue": {
                    "number": 20,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
            {
                "event": "merged",
                "created_at": "2026-09-06T11:00:00Z",
                "issue": {
                    "number": 20,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
            {
                "event": "closed",
                "created_at": "2026-09-06T11:00:01Z",
                "issue": {
                    "number": 20,
                    "pull_request": {"url": "https://api.github.com/example"},
                },
            },
        ]

        rows = build_repository_rows(
            repository,
            date(2026, 9, 5),
            date(2026, 9, 6),
            [],
            [],
            lifecycle_events,
            {
                "issues_opened",
                "issues_closed",
                "prs_opened",
                "prs_merged",
                "prs_closed_unmerged",
            },
        )

        self.assertEqual(rows[0]["prs_closed_unmerged"], 1)
        self.assertEqual(rows[1]["prs_merged"], 1)
        self.assertEqual(rows[1]["prs_closed_unmerged"], 0)

    def test_history_merge_replaces_recollected_repository_days(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "community_lifecycle_daily.csv"
            base = {
                "date": "2026-09-05",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "issues_opened": 1,
                "issues_closed": 0,
                "prs_opened": 0,
                "prs_merged": 0,
                "prs_closed_unmerged": 0,
            }
            merge_and_write(output, [base])
            replacement = dict(base)
            replacement["issues_opened"] = 2
            replacement["issues_closed"] = 1
            merge_and_write(output, [replacement])

            text = output.read_text(encoding="utf-8")
            self.assertEqual(text.count("2026-09-05"), 1)
            self.assertIn(",2,1,0,0,0", text)


if __name__ == "__main__":
    unittest.main()
