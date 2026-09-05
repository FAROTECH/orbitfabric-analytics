import tempfile
import unittest
from pathlib import Path

from analytics.community_compare import (
    build_latest_comparison,
    load_comparison_policy,
    read_history,
    write_comparison,
)


class CommunityComparisonTests(unittest.TestCase):
    def test_policy_accepts_supported_comparison_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            policy = Path(tmp) / "community-signals.yml"
            policy.write_text(
                """version: 1
comparison:
  mode: latest_vs_previous_available
  absolute_delta: true
  percentage_delta: false
  expose_snapshot_gap_days: true
""",
                encoding="utf-8",
            )
            self.assertIsNone(load_comparison_policy(policy))

    def test_first_snapshot_is_not_comparable(self) -> None:
        rows = [
            {
                "date": "2026-09-05",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "stars_total": "6",
                "forks_total": "1",
                "open_issues_total": "3",
                "open_pull_requests_total": "0",
                "contributors_repo_count": "1",
            }
        ]

        comparison = build_latest_comparison(rows)
        self.assertEqual(len(comparison), 1)
        row = comparison[0]
        self.assertEqual(row["current_date"], "2026-09-05")
        self.assertEqual(row["previous_date"], "")
        self.assertEqual(row["snapshot_gap_days"], "")
        self.assertEqual(row["comparable"], "false")
        self.assertEqual(row["stars_total"], 6)
        self.assertEqual(row["stars_total_delta"], "")

    def test_latest_snapshot_uses_previous_available_snapshot(self) -> None:
        rows = [
            {
                "date": "2026-09-03",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "stars_total": "5",
                "forks_total": "1",
                "open_issues_total": "4",
                "open_pull_requests_total": "1",
                "contributors_repo_count": "1",
            },
            {
                "date": "2026-09-05",
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "stars_total": "6",
                "forks_total": "1",
                "open_issues_total": "3",
                "open_pull_requests_total": "0",
                "contributors_repo_count": "2",
            },
        ]

        row = build_latest_comparison(rows)[0]
        self.assertEqual(row["previous_date"], "2026-09-03")
        self.assertEqual(row["snapshot_gap_days"], 2)
        self.assertEqual(row["comparable"], "true")
        self.assertEqual(row["stars_total_delta"], 1)
        self.assertEqual(row["forks_total_delta"], 0)
        self.assertEqual(row["open_issues_total_delta"], -1)
        self.assertEqual(row["open_pull_requests_total_delta"], -1)
        self.assertEqual(row["contributors_repo_count_delta"], 1)

    def test_round_trip_csv_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "community_comparison_latest.csv"
            write_comparison(
                output,
                build_latest_comparison(
                    [
                        {
                            "date": "2026-09-05",
                            "repository_id": "studio",
                            "repository": "FAROTECH/orbitfabric-studio",
                            "category": "product",
                            "stars_total": "0",
                            "forks_total": "0",
                            "open_issues_total": "2",
                            "open_pull_requests_total": "0",
                            "contributors_repo_count": "2",
                        }
                    ]
                ),
            )
            text = output.read_text(encoding="utf-8")
            self.assertIn("stars_total_delta", text)
            self.assertIn("studio", text)

            history = root / "community_daily.csv"
            history.write_text(
                "date,repository_id,repository,category,stars_total,forks_total,open_issues_total,open_pull_requests_total,contributors_repo_count\n"
                "2026-09-05,studio,FAROTECH/orbitfabric-studio,product,0,0,2,0,2\n",
                encoding="utf-8",
            )
            self.assertEqual(read_history(history)[0]["repository_id"], "studio")


if __name__ == "__main__":
    unittest.main()
