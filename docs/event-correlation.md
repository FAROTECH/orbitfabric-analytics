# Event correlation

Status: M2 foundation in progress.

## Goal

OrbitFabric Analytics records relevant ecosystem events so that traffic changes can be inspected together with known project activity.

The event layer provides context only. Temporal proximity is evidence of correlation, not proof of causation.

## Authoritative source

Events are authored in:

```text
config/events.yml
```

Policy values are defined separately in:

```text
config/event-taxonomy.yml
```

This keeps the project rule unchanged:

> policy in configuration, logic in tooling.

## Event contract

Each event has a stable identifier and a date, classification, channel, scope and confidence level.

Example:

```yaml
- id: orbitfabric-public-update
  date: 2026-09-05
  type: outreach
  channel: linkedin
  scope:
    - ecosystem
  confidence: confirmed
  label: OrbitFabric public update
```

Optional fields:

```yaml
url: https://example.invalid
notes: Additional context
```

## Scope semantics

`ecosystem` means that the event is relevant to OrbitFabric as a whole.

Repository-specific scopes use the stable repository IDs from `config/repositories.yml`, for example:

```text
core
studio
fprime-adapter
```

The validator rejects unknown repository scopes so that historical events cannot silently drift away from the repository inventory.

## Confidence

Two confidence levels are intentionally supported in M2:

```text
confirmed
approximate
```

`confirmed` means the event date is known well enough for day-level correlation.

`approximate` means the date is intentionally uncertain. Approximate historical events may still be useful as context, but they must not be interpreted with the same precision as confirmed events.

## Normalization

`analytics/events.py` validates the authored event registry against the taxonomy and repository inventory and produces:

```text
analytics/events_normalized.json
```

on the `github-repo-stats` data branch.

The normalized dataset is sorted by date and stable event ID and is the downstream source for future dashboard correlation views.

## Current M2 boundary

The first M2 increment establishes the event contract and normalized data pipeline only.

The next increment will project these events into the dashboard timeline and then add correlation-oriented views around traffic changes.

No historical outreach event should be invented merely to populate the dashboard. Events are added only when their date and meaning are known well enough to be useful.
