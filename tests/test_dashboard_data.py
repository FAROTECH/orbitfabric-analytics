import json
import tempfile
import unittest
from pathlib import Path

from analytics.dashboard_data import build_dashboard_payload, write_dashboard_payload


class DashboardDataTests(unittest.TestCase):
    def test_selects_latest_complete_day_and_builds_snapshot_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollups = root / "rollups.csv"
            comparison = root / "comparison.csv"
            daily = root / "daily.csv"

            rollups.write_text(
                "date,scope_type,scope_id,repositories_expected,repositories_available,coverage_pct,coverage_complete,clones_total,views_total,clones_unique_repo_sum,views_unique_repo_sum\n"
                "2026-09-02,ecosystem,ecosystem,2,2,100.0,True,40,7,8,3\n"
                "2026-09-02,category,core,1,1,100.0,True,20,4,4,2\n"
                "2026-09-02,category,product,1,1,100.0,True,20,3,4,1\n"
                "2026-09-03,ecosystem,ecosystem,2,2,100.0,True,130,30,25,6\n"
                "2026-09-03,category,core,1,1,100.0,True,80,16,15,4\n"
                "2026-09-03,category,product,1,1,100.0,True,50,14,10,2\n"
                "2026-09-04,ecosystem,ecosystem,2,1,50.0,False,25,5,4,1\n"
                "2026-09-04,category,core,1,1,100.0,True,25,5,4,1\n",
                encoding="utf-8",
            )

            comparison.write_text(
                "window_start,window_end,window_days,repository_id,repository,category,days_expected,days_available,coverage_pct,coverage_complete,clones_total,views_total,clones_unique_repo_day_sum,views_unique_repo_day_sum,clone_active_days,view_active_days,clone_only_days,view_only_days,mixed_days,inactive_days,clones_per_repo_day_unique,views_per_repo_day_unique,clone_to_view_ratio\n"
                "2026-09-02,2026-09-03,2,core,FAROTECH/orbitfabric,core,2,2,100.0,True,100,20,20,5,2,2,0,0,2,0,5.0,4.0,5.0\n"
                "2026-09-02,2026-09-03,2,studio,FAROTECH/orbitfabric-studio,product,2,2,100.0,True,30,10,10,2,2,1,1,0,1,0,3.0,5.0,3.0\n",
                encoding="utf-8",
            )

            daily.write_text(
                "date,repository_id,repository,category,include_in_rollups,clones_total,clones_unique,views_total,views_unique\n"
                "2026-09-01,core,FAROTECH/orbitfabric,core,True,10,2,1,1\n"
                "2026-09-01,studio,FAROTECH/orbitfabric-studio,product,True,5,1,0,0\n"
                "2026-09-02,core,FAROTECH/orbitfabric,core,True,20,4,4,2\n"
                "2026-09-02,studio,FAROTECH/orbitfabric-studio,product,True,5,1,0,0\n"
                "2026-09-03,core,FAROTECH/orbitfabric,core,True,80,14,16,3\n"
                "2026-09-03,studio,FAROTECH/orbitfabric-studio,product,True,25,8,10,2\n",
                encoding="utf-8",
            )

            payload = build_dashboard_payload(rollups, comparison, daily)

            self.assertEqual(payload["latest_complete_day"], "2026-09-03")
            self.assertEqual(payload["overview"]["clones_total"], 130)
            self.assertEqual(payload["overview_delta"]["reference_day"], "2026-09-02")
            self.assertEqual(payload["overview_delta"]["clones_total"]["absolute"], 90)
            self.assertEqual(payload["overview_delta"]["clones_total"]["pct"], 225.0)
            self.assertEqual(len(payload["latest_categories"]), 2)

            comparison_payload = payload["comparison"]
            self.assertEqual(comparison_payload["window_days"], 2)
            self.assertEqual(comparison_payload["previous_window_start"], "2026-09-01")
            self.assertEqual(comparison_payload["previous_window_end"], "2026-09-02")
            self.assertEqual(len(comparison_payload["repositories"]), 2)

            core = comparison_payload["repositories"][0]
            self.assertEqual(core["repository_id"], "core")
            self.assertTrue(core["delta"]["comparable"])
            self.assertEqual(core["delta"]["clones_total"]["previous"], 30)
            self.assertEqual(core["delta"]["clones_total"]["absolute"], 70)
            self.assertEqual(core["delta"]["clones_total"]["pct"], 233.3)
            self.assertEqual(core["delta"]["views_total"]["previous"], 5)
            self.assertEqual(core["delta"]["views_total"]["absolute"], 15)

            studio = comparison_payload["repositories"][1]
            self.assertEqual(studio["repository_id"], "studio")
            self.assertEqual(studio["delta"]["views_total"]["state"], "new")
            self.assertIsNone(studio["delta"]["views_total"]["pct"])

            output = root / "dashboard_data.json"
            write_dashboard_payload(payload, output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written["latest_complete_day"], "2026-09-03")
            self.assertEqual(written["comparison"]["window_end"], "2026-09-03")
            self.assertEqual(
                written["comparison"]["repositories"][0]["delta"]["clones_total"]["absolute"],
                70,
            )


if __name__ == "__main__":
    unittest.main()
