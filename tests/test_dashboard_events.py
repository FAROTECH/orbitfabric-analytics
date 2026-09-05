import json
import tempfile
import unittest
from pathlib import Path

from analytics.dashboard_events import project_events, write_dashboard


class DashboardEventProjectionTests(unittest.TestCase):
    def test_projects_timeline_events_and_tracks_pending_context(self) -> None:
        dashboard = {
            "schema_version": 1,
            "latest_complete_day": "2026-09-04",
            "timeline": [
                {"date": "2026-09-03", "ecosystem": {}, "categories": {}},
                {"date": "2026-09-04", "ecosystem": {}, "categories": {}},
            ],
        }
        events = {
            "schema_version": 1,
            "events": [
                {
                    "id": "before-window",
                    "date": "2026-09-02",
                    "type": "release",
                    "channel": "github",
                    "scope": ["ecosystem"],
                    "confidence": "confirmed",
                    "label": "Older event",
                },
                {
                    "id": "in-window",
                    "date": "2026-09-04",
                    "type": "upstream-discussion",
                    "channel": "github",
                    "scope": ["ecosystem"],
                    "confidence": "confirmed",
                    "label": "Current event",
                },
                {
                    "id": "pending",
                    "date": "2026-09-05",
                    "type": "upstream-discussion",
                    "channel": "libre-space",
                    "scope": ["ecosystem"],
                    "confidence": "confirmed",
                    "label": "Pending event",
                },
            ],
        }

        projected = project_events(dashboard, events)

        self.assertEqual(projected["event_context"]["timeline_start"], "2026-09-03")
        self.assertEqual(projected["event_context"]["timeline_end"], "2026-09-04")
        self.assertEqual(projected["event_context"]["events_total"], 3)
        self.assertEqual(projected["event_context"]["events_in_timeline"], 1)
        self.assertEqual(projected["event_context"]["events_pending"], 1)
        self.assertEqual(projected["event_context"]["events_before_timeline"], 1)
        self.assertEqual(projected["timeline"][0]["events"], [])
        self.assertEqual(projected["timeline"][1]["events"][0]["id"], "in-window")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dashboard_data.json"
            write_dashboard(projected, output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written["events"][2]["id"], "pending")
            self.assertEqual(written["timeline"][1]["events"][0]["id"], "in-window")


if __name__ == "__main__":
    unittest.main()
