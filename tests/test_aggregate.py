import csv
import tempfile
import unittest
from pathlib import Path

from analytics.aggregate import build_dataset, write_dataset


class AggregateDatasetTests(unittest.TestCase):
    def test_builds_repo_day_rows_and_skips_disabled_repositories(self) -> None:
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
  - id: disabled
    repo: FAROTECH/disabled
    category: legacy
    collect: false
    include_in_rollups: false
""".strip()
                + "\n",
                encoding="utf-8",
            )

            source = root / "data" / "FAROTECH" / "orbitfabric" / "ghrs-data"
            source.mkdir(parents=True)
            (source / "views_clones_aggregate.csv").write_text(
                "time_iso8601,clones_total,clones_unique,views_total,views_unique\n"
                "2026-09-03 00:00:00+00:00,10,3,7,2\n",
                encoding="utf-8",
            )

            rows = build_dataset(config, root / "data")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["date"], "2026-09-03")
            self.assertEqual(rows[0]["repository_id"], "core")
            self.assertEqual(rows[0]["category"], "core")
            self.assertTrue(rows[0]["include_in_rollups"])
            self.assertEqual(rows[0]["clones_total"], 10)
            self.assertEqual(rows[0]["clones_unique"], 3)

            output = root / "out" / "ecosystem_daily.csv"
            write_dataset(rows, output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                written = list(csv.DictReader(handle))

            self.assertEqual(len(written), 1)
            self.assertEqual(written[0]["repository"], "FAROTECH/orbitfabric")


if __name__ == "__main__":
    unittest.main()
