import json
import tempfile
import unittest
from pathlib import Path

from analytics.dashboard_referrers import project_referrers
from analytics.referrers import build_referrer_aggregate


class ReferrerAnalyticsTests(unittest.TestCase):
    def test_aggregates_latest_official_repository_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "repositories.yml"
            data = root / "data"
            dashboard = root / "dashboard.json"
            aggregate = root / "referrers.json"

            config.write_text(
                """version: 1
repositories:
  - id: core
    repo: OrbitFabric/orbitfabric
    category: core
    collect: true
    include_in_rollups: true
  - id: studio
    repo: OrbitFabric/orbitfabric-studio
    category: product
    collect: true
    include_in_rollups: true
  - id: ignored
    repo: OrbitFabric/ignored
    category: ecosystem
    collect: true
    include_in_rollups: false
""",
                encoding="utf-8",
            )

            def write_history(repository: str, snapshots: dict[str, list[dict[str, object]]]) -> None:
                path = data / repository / "ghrs-data" / "referrers_history.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "window_days": 14,
                            "snapshots": snapshots,
                        }
                    ),
                    encoding="utf-8",
                )

            write_history(
                "OrbitFabric/orbitfabric",
                {
                    "2026-09-22": [
                        {"referrer": "github.com", "views": 20, "unique_visitors": 2}
                    ],
                    "2026-09-23": [
                        {"referrer": "github.com", "views": 22, "unique_visitors": 2},
                        {"referrer": "reddit.com", "views": 1, "unique_visitors": 1},
                    ],
                },
            )
            write_history(
                "OrbitFabric/orbitfabric-studio",
                {
                    "2026-09-23": [
                        {"referrer": "github.com", "views": 5, "unique_visitors": 1},
                        {"referrer": "google.com", "views": 3, "unique_visitors": 2},
                    ]
                },
            )
            write_history(
                "OrbitFabric/ignored",
                {
                    "2026-09-23": [
                        {"referrer": "ignored.example", "views": 99, "unique_visitors": 99}
                    ]
                },
            )

            payload = build_referrer_aggregate(config, data)
            self.assertEqual(payload["repositories_expected"], 2)
            self.assertEqual(payload["repositories_available"], 2)
            self.assertEqual(payload["snapshot_date_max"], "2026-09-23")
            self.assertEqual(payload["rows"][0]["site"], "github.com")
            self.assertEqual(payload["rows"][0]["views"], 27)
            self.assertEqual(payload["rows"][0]["unique_visitors_repo_sum"], 3)
            self.assertEqual(payload["rows"][0]["repositories"], 2)
            self.assertNotIn(
                "ignored.example",
                {row["site"] for row in payload["rows"]},
            )

            aggregate.write_text(json.dumps(payload), encoding="utf-8")
            dashboard.write_text(
                json.dumps({"schema_version": 1, "latest_complete_day": "2026-09-21"}),
                encoding="utf-8",
            )
            projected = project_referrers(dashboard, aggregate)
            self.assertEqual(projected["referrers"]["rows"][0]["site"], "github.com")


if __name__ == "__main__":
    unittest.main()
