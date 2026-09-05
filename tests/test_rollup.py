import csv
import tempfile
import unittest
from pathlib import Path

from analytics.rollup import build_rollups, write_rollups


class RollupDatasetTests(unittest.TestCase):
    def test_builds_official_rollups_with_explicit_coverage(self) -> None:
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
  - id: fprime-adapter
    repo: FAROTECH/orbitfabric-fprime-adapter
    category: adapter
    collect: true
    include_in_rollups: true
  - id: adapter-catalog
    repo: FAROTECH/orbitfabric-adapter-catalog
    category: ecosystem
    collect: true
    include_in_rollups: false
""".strip()
                + "\n",
                encoding="utf-8",
            )

            normalized = root / "ecosystem_daily.csv"
            normalized.write_text(
                "date,repository_id,repository,category,include_in_rollups,"
                "clones_total,clones_unique,views_total,views_unique\n"
                "2026-09-01,core,FAROTECH/orbitfabric,core,True,10,3,7,2\n"
                "2026-09-01,studio,FAROTECH/orbitfabric-studio,product,True,0,0,0,0\n"
                "2026-09-01,fprime-adapter,FAROTECH/orbitfabric-fprime-adapter,adapter,True,20,4,5,1\n"
                "2026-09-01,adapter-catalog,FAROTECH/orbitfabric-adapter-catalog,ecosystem,False,99,20,99,20\n"
                "2026-09-02,core,FAROTECH/orbitfabric,core,True,6,2,4,1\n"
                "2026-09-02,studio,FAROTECH/orbitfabric-studio,product,True,4,1,0,0\n"
                "2026-09-02,adapter-catalog,FAROTECH/orbitfabric-adapter-catalog,ecosystem,False,50,10,50,10\n",
                encoding="utf-8",
            )

            rows = build_rollups(config, normalized)
            by_key = {
                (str(row["date"]), str(row["scope_type"]), str(row["scope_id"])): row
                for row in rows
            }

            ecosystem_day_1 = by_key[("2026-09-01", "ecosystem", "ecosystem")]
            self.assertEqual(ecosystem_day_1["repositories_expected"], 3)
            self.assertEqual(ecosystem_day_1["repositories_available"], 3)
            self.assertEqual(ecosystem_day_1["coverage_pct"], 100.0)
            self.assertTrue(ecosystem_day_1["coverage_complete"])
            self.assertEqual(ecosystem_day_1["clones_total"], 30)
            self.assertEqual(ecosystem_day_1["views_total"], 12)
            self.assertEqual(ecosystem_day_1["clones_unique_repo_sum"], 7)
            self.assertEqual(ecosystem_day_1["views_unique_repo_sum"], 3)

            ecosystem_day_2 = by_key[("2026-09-02", "ecosystem", "ecosystem")]
            self.assertEqual(ecosystem_day_2["repositories_expected"], 3)
            self.assertEqual(ecosystem_day_2["repositories_available"], 2)
            self.assertEqual(ecosystem_day_2["coverage_pct"], 66.67)
            self.assertFalse(ecosystem_day_2["coverage_complete"])
            self.assertEqual(ecosystem_day_2["clones_total"], 10)
            self.assertEqual(ecosystem_day_2["views_total"], 4)

            adapter_day_2 = by_key[("2026-09-02", "category", "adapter")]
            self.assertEqual(adapter_day_2["repositories_expected"], 1)
            self.assertEqual(adapter_day_2["repositories_available"], 0)
            self.assertEqual(adapter_day_2["coverage_pct"], 0.0)
            self.assertFalse(adapter_day_2["coverage_complete"])
            self.assertEqual(adapter_day_2["clones_total"], 0)
            self.assertEqual(adapter_day_2["views_total"], 0)

            product_day_1 = by_key[("2026-09-01", "category", "product")]
            self.assertEqual(product_day_1["repositories_available"], 1)
            self.assertEqual(product_day_1["coverage_pct"], 100.0)
            self.assertEqual(product_day_1["clones_total"], 0)

            self.assertNotIn(("2026-09-01", "category", "ecosystem"), by_key)

            output = root / "ecosystem_rollups_daily.csv"
            write_rollups(rows, output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                written = list(csv.DictReader(handle))

            self.assertEqual(len(written), len(rows))
            self.assertEqual(written[0]["scope_type"], "ecosystem")


if __name__ == "__main__":
    unittest.main()
