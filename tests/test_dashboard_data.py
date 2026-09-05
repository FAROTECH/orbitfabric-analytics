import json
import tempfile
import unittest
from pathlib import Path

from analytics.dashboard_data import build_dashboard_payload, write_dashboard_payload


class DashboardDataTests(unittest.TestCase):
    def test_selects_latest_complete_day_and_builds_presentation_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollups = root / "rollups.csv"
            comparison = root / "comparison.csv"

            rollups.write_text(
                "date,scope_type,scope_id,repositories_expected,repositories_available,coverage_pct,coverage_complete,clones_total,views_total,clones_unique_repo_sum,views_unique_repo_sum\n"
                "2026-09-03,ecosystem,ecosystem,2,2,100.0,True,100,20,15,4\n"
                "2026-09-03,category,core,1,1,100.0,True,70,10,8,2\n"
                "2026-09-03,category,product,1,1,100.0,True,30,10,7,2\n"
                "2026-09-04,ecosystem,ecosystem,2,1,50.0,False,25,5,4,1\n"
                "2026-09-04,category,core,1,1,100.0,True,25,5,4,1\n",
                encoding="utf-8",
            )

            comparison.write_text(
                "window_start,window_end,window_days,repository_id,repository,category,days_expected,days_available,coverage_pct,coverage_complete,clones_total,views_total,clones_unique_repo_day_sum,views_unique_repo_day_sum,clone_active_days,view_active_days,clone_only_days,view_only_days,mixed_days,inactive_days,clones_per_repo_day_unique,views_per_repo_day_unique,clone_to_view_ratio\n"
                "2026-08-21,2026-09-03,14,core,FAROTECH/orbitfabric,core,14,14,100.0,True,100,20,25,4,10,5,5,0,5,4,4.0,5.0,5.0\n"
                "2026-08-21,2026-09-03,14,studio,FAROTECH/orbitfabric-studio,product,14,14,100.0,True,30,10,10,2,5,3,2,0,3,9,3.0,5.0,3.0\n",
                encoding="utf-8",
            )

            payload = build_dashboard_payload(rollups, comparison)

            self.assertEqual(payload["latest_complete_day"], "2026-09-03")
            self.assertEqual(payload["overview"]["clones_total"], 100)
            self.assertEqual(len(payload["latest_categories"]), 2)
            self.assertEqual(payload["comparison"]["window_days"], 14)
            self.assertEqual(len(payload["comparison"]["repositories"]), 2)

            output = root / "dashboard_data.json"
            write_dashboard_payload(payload, output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written["latest_complete_day"], "2026-09-03")
            self.assertEqual(written["comparison"]["window_end"], "2026-09-03")


if __name__ == "__main__":
    unittest.main()
