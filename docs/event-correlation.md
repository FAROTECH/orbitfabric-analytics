# Event correlation

Status: M2 in progress.

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

The normalized dataset is sorted by date and stable event ID.

## Dashboard projection

`analytics/dashboard_events.py` projects normalized events into the generated dashboard payload after the normal traffic payload has been built.

The projection adds:

```text
events
event_context
timeline[].events
```

`event_context` explicitly separates three cases:

```text
events_in_timeline
    event date has retained traffic data and can be inspected in context

events_pending
    event is newer than the latest complete traffic day

events_before_timeline
    event predates the currently retained dashboard window
```

This distinction is important. A newly authored event can appear in the dashboard immediately without pretending that traffic correlation is already available for that day.

## Traffic/event inspection

The dashboard uses a mobile-first event rail instead of permanently drawing event lines across every chart.

The default state stays visually quiet:

```text
traffic charts
    no persistent event lines

event rail
    compact markers grouped by day
```

Selecting an in-window event marker, or the `Show on charts` action on an event card, draws a thin dashed guide for that day on both Clone activity and View activity charts. Selecting the same day again clears the guide.

This interaction is intentionally on-demand so that 14-day charts remain readable on small screens. The event rail remains the persistent orientation surface, while the chart guide appears only during inspection.

Events newer than the latest complete traffic day are shown separately as `awaiting traffic`. They remain visible as context, but no chart guide is drawn until the corresponding traffic day exists.

## Current M2 boundary

The event registry, normalization pipeline, dashboard projection and direct on-demand traffic/event inspection are implemented.

The remaining work is to validate the interactive overlay end to end in deployment and perform the first explicit traffic/event correlation review using real retained traffic data.

No historical outreach event should be invented merely to populate the dashboard. Events are added only when their date and meaning are known well enough to be useful.
