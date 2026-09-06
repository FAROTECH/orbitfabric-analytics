# Operational Milestone 1 - Ecosystem Observability Baseline

Status: final validation pending.

## Purpose

This milestone defines the first point at which OrbitFabric Analytics can be left running as a durable operational baseline while product development, adapter work and community activity continue independently.

The milestone is deliberately not a claim that analytics is feature-complete. It is the point where the evidence pipeline, semantic boundaries and dashboard are sufficiently coherent to preserve useful history and support later interpretation without requiring immediate expansion.

## Included capability

```text
M0  traffic retention
M1  ecosystem traffic dashboard
M2  curated event correlation
M3a community stock
M3b community stock deltas
M3c development activity context
M3d issue / PR lifecycle
M3e repository participation baseline
M3f community + engineering dashboard context
```

The operational evidence model is:

```text
TRAFFIC
        +
COMMUNITY STOCK
        +
LIFECYCLE
        +
PARTICIPATION
        +
DEVELOPMENT CONTEXT
        +
CURATED CONTEXT
        ↓
ECOSYSTEM OBSERVABILITY
```

These evidence families remain semantically separate. The dashboard makes them inspectable together without turning correlation into attribution or repository-scoped identities into ecosystem-wide users.

## Dashboard boundary

The first-milestone dashboard provides:

- traffic overview and deltas;
- clone and view timelines;
- curated event correlation;
- current community stock and stock deltas;
- lifecycle, participation and development context aligned to the common traffic comparison window;
- repository-level ecosystem context;
- repository traffic comparison and signal shape.

Community stock is allowed to be newer than the latest complete traffic day and exposes its own observation date.

The raw participant actor registry remains private and is not published with the dashboard.

## Deferred by design

The following capabilities are intentionally not required for this milestone:

```text
PR review participation
GitHub Discussions
reactions
richer participant / contributor analysis
longer rolling-trend semantics
web / documentation analytics
automated intelligence and anomaly detection
```

They remain roadmap TODO items and can be added when the amount of real ecosystem activity justifies them.

## Closure criteria

Completed:

- collection and retained data branches are operational;
- traffic, event, community, lifecycle, participation and development collectors are validated;
- semantic interpretation boundaries are documented;
- dashboard M3f source and payload projection are implemented;
- PWA deployment architecture is operational and mobile capable.

Pending final closure:

```text
1. one green workflow run containing M3f dashboard projection
2. resulting dashboard-site deployment confirmed
3. final desktop/mobile presentation check
```

After those checks this document can be marked `Status: complete` and the analytics project can return to normal scheduled operation until the next roadmap increment is intentionally opened.
