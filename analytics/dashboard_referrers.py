#!/usr/bin/env python3
"""Project aggregated GitHub referrers into the static dashboard payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def project_referrers(
    dashboard_path: Path,
    referrers_path: Path,
) -> dict[str, object]:
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    referrers = json.loads(referrers_path.read_text(encoding="utf-8"))
    dashboard["referrers"] = referrers
    return dashboard


def write_dashboard(payload: dict[str, object], dashboard_path: Path) -> None:
    dashboard_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project GitHub referrers into the dashboard payload."
    )
    parser.add_argument("--dashboard", type=Path, required=True)
    parser.add_argument("--referrers", type=Path, required=True)
    args = parser.parse_args()

    payload = project_referrers(args.dashboard, args.referrers)
    write_dashboard(payload, args.dashboard)
    print(f"Projected referrers into {args.dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
