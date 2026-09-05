import csv
import tempfile
import unittest
from pathlib import Path

from analytics.compare import build_comparison, write_comparison


class RepositoryComparisonTests(unittest.TestCase):
    def test_anchors_to_latest_complete_day_and_tracks_window_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "repositories.yml"
            config.write_text(
                """
version: 1
repositories:
  - id: core
    repo: FAROTECH/orbitfabric
    category: core
    collect: true
    include_in_rollups: true
  - id: studio
    repo: FAROTECH/orbitfabric-studio
    category: product
    collect: true
    include_in_rollups: true
  - id: technical
    repo: FAROTECH/orbitfabric-adapter-template
    category: ecosystem
    collect: true
    include_in_rollups: false
""".strip()
                + "\n",
                encoding="utf-8",
            )

            daily = root / "ecosystem_daily.csv"
            daily.write_text(
                "date,repository_id,repository,category,include_in_rollups,"
                "clones_total,clones_unique,views_total,views_unique\n"
                "2026-09-02,core,FAROTECH/orbitfabric,core,True,10,2,0,0\n"
                "2026-09-02,technical,FAROTECH/orbitfabric-adapter-template,ecosystem,False,99,9,99,9\n"
                "2026-09-03,core,FAROTECH/orbitfabric,core,True,4,1,5,2\n"
                "2026-09-03,studio,FAROTECH/orbitfabric-studio,product,True,0,0,7,3\n"
                "2026-09-04,core,FAROTECH/orbitfabric,core,True,1000,100,1000,100\n"
                "2026-09-04,studio,FAROTECH/orbitfabric-studio,product,True,1000,100,1000,100\n",
                encoding="utf-8",
            )

            rollups = root / "ecosystem_rollups_daily.csv"
            rollups.write_text(
                "date,scope_type,scope_id,repositories_expected,repositories_available,"
                "coverage_pct,coverage_complete,clones_total,views_total,"
                "clones_unique_repo_sum,views_unique_repo_sum\n"
                "2026-09-02,ecosystem,ecosystem,2,2,100.0,True,10,0,2,0\n"
                "2026-09-03,ecosystem,ecosystem,2,2,100.0,True,4,12,1,5\n"
                "2026-09-04,ecosystem,ecosystem,2,1,50.0,False,1000,1000,100,100\n",
                encoding="utf-8",
            )

            rows = build_comparison(
                config,
                daily,
                rollups,
                window_days=2,
            )

            self.assertEqual(len(rows), 2)

            core = rows[0]
            self.assertEqual(core["repository_id"], "core")
            self.assertEqual(core["window_start"], "2026-09-02")
            self.assertEqual(core["window_end"], "2026-09-03")
            self.assertEqual(core["days_available"], 2)
            self.assertEqual(core["coverage_pct"], 100.0)
            self.assertTrue(core["coverage_complete"])
            self.assertEqual(core["clones_total"], 14)
            self.assertEqual(core["views_total"], 5)
            self.assertEqual(core["clones_unique_repo_day_sum"], 3)
            self.assertEqual(core["views_unique_repo_day_sum"], 2)
            self.assertEqual(core["clone_active_days"], 2)
            self.assertEqual(core["view_active_days"], 1)
            self.assertEqual(core["clone_only_days"], 1)
            self.assertEqual(core["mixed_days"], 1)
            self.assertEqual(core["clones_per_repo_day_unique"], 4.67)
            self.assertEqual(core["views_per_repo_day_unique"], 2.5)
            self.assertEqual(core["clone_to_view_ratio"], 2.8)

            studio = rows[1]
            self.assertEqual(studio["repository_id"], "studio")
            self.assertEqual(studio["days_available"], 1)
            self.assertEqual(studio["coverage_pct"], 50.0)
            self.assertFalse(studio["coverage_complete"])
            self.assertEqual(studio["clones_total"], 0)
            self.assertEqual(studio["views_total"], 7)
            self.assertEqual(studio["view_only_days"], 1)
            self.assertEqual(studio["inactive_days"], 0)
            self.assertEqual(studio["clone_to_view_ratio"], 0.0)

            output = root / "repository_comparison_latest.csv"
            write_comparison(rows, output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                written = list(csv.DictReader(handle))

            self.assertEqual(len(written), 2)
            self.assertEqual(written[0]["window_end"], "2026-09-03")
            self.assertEqual(written[1]["coverage_pct"], "50.0")


if __name__ == "__main__":
    unittest.main()
