import tempfile
import unittest
from datetime import date
from pathlib import Path

from analytics.development_activity import (
    build_repository_rows,
    load_policy,
    merge_and_write,
)


class DevelopmentActivityTests(unittest.TestCase):
    def test_policy_selects_official_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repositories = root / "repositories.yml"
            policy = root / "development-activity.yml"

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
  automation_logins: [github-actions[bot]]
""",
                encoding="utf-8",
            )

            selected, days, first_party, automation = load_policy(repositories, policy)
            self.assertEqual([item["id"] for item in selected], ["core"])
            self.assertEqual(days, 21)
            self.assertEqual(first_party, {"FAROTECH"})
            self.assertEqual(automation, {"github-actions[bot]"})

    def test_build_rows_classifies_commits_and_workflow_runs(self) -> None:
        repository = {
            "id": "core",
            "repo": "FAROTECH/orbitfabric",
            "category": "core",
        }
        commits = [
            {
                "author": {"login": "FAROTECH"},
                "committer": {"login": "web-flow"},
                "commit": {"author": {"date": "2026-09-05T10:00:00Z"}},
            },
            {
                "author": {"login": "github-actions[bot]"},
                "committer": {"login": "github-actions[bot]"},
                "commit": {"author": {"date": "2026-09-05T11:00:00Z"}},
            },
            {
                "author": None,
                "committer": None,
                "commit": {"author": {"date": "2026-09-06T09:00:00Z"}},
            },
        ]
        runs = [
            {"created_at": "2026-09-05T12:00:00Z", "conclusion": "success"},
            {"created_at": "2026-09-05T13:00:00Z", "conclusion": "failure"},
            {"created_at": "2026-09-06T08:00:00Z", "conclusion": "cancelled"},
        ]

        rows = build_repository_rows(
            repository,
            "main",
            date(2026, 9, 5),
            date(2026, 9, 6),
            commits,
            runs,
            {"FAROTECH"},
            {"github-actions[bot]"},
        )

        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first["commits_total"], 2)
        self.assertEqual(first["first_party_commits"], 1)
        self.assertEqual(first["automation_commits"], 1)
        self.assertEqual(first["other_commits"], 0)
        self.assertEqual(first["workflow_runs_total"], 2)
        self.assertEqual(first["workflow_runs_success"], 1)
        self.assertEqual(first["workflow_runs_failure"], 1)
        self.assertEqual(first["workflow_runs_other"], 0)

        second = rows[1]
        self.assertEqual(second["commits_total"], 1)
        self.assertEqual(second["other_commits"], 1)
        self.assertEqual(second["workflow_runs_total"], 1)
        self.assertEqual(second["workflow_runs_other"], 1)

    def test_history_merge_replaces_recollected_repository_days(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "development_activity_daily.csv"
            base = {
                "date": "2026-09-05",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "default_branch": "main",
                "commits_total": 1,
                "first_party_commits": 1,
                "automation_commits": 0,
                "other_commits": 0,
                "workflow_runs_total": 2,
                "workflow_runs_success": 2,
                "workflow_runs_failure": 0,
                "workflow_runs_other": 0,
            }
            merge_and_write(output, [base])
            replacement = dict(base)
            replacement["commits_total"] = 3
            replacement["first_party_commits"] = 3
            merge_and_write(output, [replacement])

            text = output.read_text(encoding="utf-8")
            self.assertEqual(text.count("2026-09-05"), 1)
            self.assertIn(",3,3,0,0,", text)


if __name__ == "__main__":
    unittest.main()
