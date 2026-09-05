import csv
import tempfile
import unittest
from pathlib import Path

from analytics.community import (
    collect_snapshot,
    load_selected_repositories,
    merge_and_write,
)


class FakeApi:
    def repository(self, repository: str) -> dict[str, object]:
        values = {
            "FAROTECH/orbitfabric": {"stargazers_count": 12, "forks_count": 3},
        }
        return values[repository]

    def open_issue_count(self, repository: str) -> int:
        return 4

    def open_pull_request_count(self, repository: str) -> int:
        return 2

    def contributor_count(self, repository: str) -> int:
        return 5


class CommunitySignalTests(unittest.TestCase):
    def test_selects_official_repositories_and_collects_stock_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repositories = root / "repositories.yml"
            policy = root / "community-signals.yml"

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
signals:
  stars_total: {collect: true}
  forks_total: {collect: true}
  open_issues_total: {collect: true}
  open_pull_requests_total: {collect: true}
  contributors_repo_count: {collect: true}
""",
                encoding="utf-8",
            )

            selected, signals = load_selected_repositories(repositories, policy)
            self.assertEqual([row["id"] for row in selected], ["core"])

            rows = collect_snapshot(selected, signals, FakeApi(), "2026-09-05")
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["stars_total"], 12)
            self.assertEqual(row["forks_total"], 3)
            self.assertEqual(row["open_issues_total"], 4)
            self.assertEqual(row["open_pull_requests_total"], 2)
            self.assertEqual(row["contributors_repo_count"], 5)

    def test_same_day_snapshot_replaces_repository_row_without_losing_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "community_daily.csv"
            merge_and_write(
                output,
                [
                    {
                        "date": "2026-09-04",
                        "repository_id": "core",
                        "repository": "FAROTECH/orbitfabric",
                        "category": "core",
                        "stars_total": 10,
                        "forks_total": 2,
                        "open_issues_total": 3,
                        "open_pull_requests_total": 1,
                        "contributors_repo_count": 4,
                    },
                    {
                        "date": "2026-09-05",
                        "repository_id": "core",
                        "repository": "FAROTECH/orbitfabric",
                        "category": "core",
                        "stars_total": 11,
                        "forks_total": 2,
                        "open_issues_total": 3,
                        "open_pull_requests_total": 1,
                        "contributors_repo_count": 4,
                    },
                ],
            )
            merge_and_write(
                output,
                [
                    {
                        "date": "2026-09-05",
                        "repository_id": "core",
                        "repository": "FAROTECH/orbitfabric",
                        "category": "core",
                        "stars_total": 12,
                        "forks_total": 3,
                        "open_issues_total": 4,
                        "open_pull_requests_total": 2,
                        "contributors_repo_count": 5,
                    }
                ],
            )

            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["date"], "2026-09-04")
            self.assertEqual(rows[1]["date"], "2026-09-05")
            self.assertEqual(rows[1]["stars_total"], "12")
            self.assertEqual(rows[1]["contributors_repo_count"], "5")


if __name__ == "__main__":
    unittest.main()
