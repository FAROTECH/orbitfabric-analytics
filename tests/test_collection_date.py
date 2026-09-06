import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.collection_date import load_policy, resolve_collection_date


class CollectionDateTests(unittest.TestCase):
    def test_delayed_nightly_run_stays_on_previous_logical_day(self) -> None:
        resolved = resolve_collection_date(
            datetime(2026, 9, 5, 23, 8, tzinfo=timezone.utc),
            ZoneInfo("Europe/Rome"),
            6,
        )
        self.assertEqual(resolved, "2026-09-05")

    def test_morning_manual_run_uses_current_local_day(self) -> None:
        resolved = resolve_collection_date(
            datetime(2026, 9, 6, 6, 39, tzinfo=timezone.utc),
            ZoneInfo("Europe/Rome"),
            6,
        )
        self.assertEqual(resolved, "2026-09-06")

    def test_policy_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "collection.yml"
            path.write_text(
                "version: 1\ntimezone: Europe/Rome\nrollover_hour: 6\n",
                encoding="utf-8",
            )
            timezone_value, rollover = load_policy(path)
            self.assertEqual(timezone_value.key, "Europe/Rome")
            self.assertEqual(rollover, 6)


if __name__ == "__main__":
    unittest.main()
