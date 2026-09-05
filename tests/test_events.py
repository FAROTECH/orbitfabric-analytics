import json
import tempfile
import unittest
from pathlib import Path

from analytics.events import build_event_registry, write_event_registry


class EventRegistryTests(unittest.TestCase):
    def test_validates_and_normalizes_event_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = root / "events.yml"
            taxonomy = root / "event-taxonomy.yml"
            repositories = root / "repositories.yml"

            taxonomy.write_text(
                """
version: 1
types:
  - outreach
  - internal
channels:
  - linkedin
  - analytics
confidence_levels:
  - confirmed
  - approximate
""".strip()
                + "\n",
                encoding="utf-8",
            )

            repositories.write_text(
                """
version: 1
repositories:
  - id: core
    repo: FAROTECH/orbitfabric
    category: core
    collect: true
    include_in_rollups: true
""".strip()
                + "\n",
                encoding="utf-8",
            )

            events.write_text(
                """
version: 1
events:
  - id: public-update
    date: 2026-09-04
    type: outreach
    channel: linkedin
    scope:
      - ecosystem
      - core
    confidence: confirmed
    label: Public OrbitFabric update
  - id: analytics-start
    date: 2026-09-03
    type: internal
    channel: analytics
    scope:
      - ecosystem
    confidence: approximate
    label: Analytics collection starts
    notes: Context only
""".strip()
                + "\n",
                encoding="utf-8",
            )

            payload = build_event_registry(events, taxonomy, repositories)

            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(len(payload["events"]), 2)
            self.assertEqual(payload["events"][0]["id"], "analytics-start")
            self.assertEqual(payload["events"][1]["scope"], ["ecosystem", "core"])

            output = root / "events_normalized.json"
            write_event_registry(payload, output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written["events"][1]["channel"], "linkedin")

    def test_rejects_unknown_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "taxonomy.yml").write_text(
                "version: 1\ntypes: [outreach]\nchannels: [linkedin]\nconfidence_levels: [confirmed]\n",
                encoding="utf-8",
            )
            (root / "repositories.yml").write_text(
                "version: 1\nrepositories: []\n",
                encoding="utf-8",
            )
            (root / "events.yml").write_text(
                "version: 1\nevents:\n  - id: bad\n    date: 2026-09-04\n    type: outreach\n    channel: linkedin\n    scope: [unknown-repo]\n    confidence: confirmed\n    label: Bad scope\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Unknown event scope"):
                build_event_registry(
                    root / "events.yml",
                    root / "taxonomy.yml",
                    root / "repositories.yml",
                )


if __name__ == "__main__":
    unittest.main()
