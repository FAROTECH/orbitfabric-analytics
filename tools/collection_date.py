#!/usr/bin/env python3
"""Resolve the logical analytics collection date from configured local time policy."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


def load_policy(path: Path) -> tuple[ZoneInfo, int]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("collection.yml must contain a mapping")

    timezone_name = payload.get("timezone")
    rollover_hour = payload.get("rollover_hour")
    if not isinstance(timezone_name, str) or not timezone_name:
        raise ValueError("collection.timezone must be a non-empty string")
    if not isinstance(rollover_hour, int) or not 0 <= rollover_hour <= 23:
        raise ValueError("collection.rollover_hour must be an integer in [0, 23]")

    return ZoneInfo(timezone_name), rollover_hour


def resolve_collection_date(
    current: datetime,
    local_timezone: ZoneInfo,
    rollover_hour: int,
) -> str:
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    local = current.astimezone(local_timezone)
    if local.hour < rollover_hour:
        local -= timedelta(days=1)
    return local.date().isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the logical analytics date.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--now",
        help="Optional ISO-8601 timestamp for testing; defaults to current UTC time.",
    )
    args = parser.parse_args()

    local_timezone, rollover_hour = load_policy(args.config)
    current = (
        datetime.fromisoformat(args.now.replace("Z", "+00:00"))
        if args.now
        else datetime.now(timezone.utc)
    )
    print(resolve_collection_date(current, local_timezone, rollover_hour))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
