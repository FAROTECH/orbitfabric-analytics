import csv
import tempfile
import unittest
from pathlib import Path

from tools.collect_traffic import _read_existing, merge_metric, write_rows


class CollectTrafficTests(unittest.TestCase):
    def test_merge_preserves_history_and_overwrites_current_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "views_clones_aggregate.csv"
            path.write_text(
                "time_iso8601,clones_total,clones_unique,views_total,views_unique\n"
                "2026-09-01 00:00:00+00:00,5,2,7,3\n"
                "2026-09-02 00:00:00+00:00,1,1,1,1\n",
                encoding="utf-8",
            )

            rows = _read_existing(path)
            merge_metric(
                rows,
                "clones",
                [
                    {
                        "timestamp": "2026-09-02T00:00:00Z",
                        "count": 10,
                        "uniques": 4,
                    },
                    {
                        "timestamp": "2026-09-03T00:00:00Z",
                        "count": 8,
                        "uniques": 3,
                    },
                ],
            )
            merge_metric(
                rows,
                "views",
                [
                    {
                        "timestamp": "2026-09-02T00:00:00Z",
                        "count": 20,
                        "uniques": 6,
                    },
                    {
                        "timestamp": "2026-09-03T00:00:00Z",
                        "count": 12,
                        "uniques": 5,
                    },
                ],
            )
            write_rows(path, rows)

            with path.open(newline="", encoding="utf-8") as handle:
                result = list(csv.DictReader(handle))

            self.assertEqual(result[0]["time_iso8601"], "2026-09-01 00:00:00+00:00")
            self.assertEqual(result[0]["clones_total"], "5")
            self.assertEqual(result[1]["clones_total"], "10")
            self.assertEqual(result[1]["views_total"], "20")
            self.assertEqual(result[2]["clones_unique"], "3")
            self.assertEqual(result[2]["views_unique"], "5")


if __name__ == "__main__":
    unittest.main()
