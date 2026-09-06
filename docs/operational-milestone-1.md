# Operational Milestone 1 - Ecosystem Observability Baseline

Status: complete.

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

Participation retains aggregate repository-day evidence only. Raw actor logins are used transiently during collection and are not persisted into retained analytics state.

## Repository visibility and public-safe boundary

The durable architectural decision is that retained Analytics state is public-safe by design.

Repository visibility itself is an operational choice and may change between public and private without changing metric semantics, data-retention boundaries or the dashboard contract.

The public interval used for this milestone validated that boundary in practice and also allowed the GitHub-hosted workflow to execute without consuming private-repository Actions minutes.

Before the visibility change, the previous cumulative participant registry was removed from `github-repo-stats`. Its historical content contained only the maintainer login `FAROTECH`; no third-party identity had been retained.

Repository-scoped `first_seen` semantics are now reconstructed from public GitHub events since the fixed observation baseline rather than from a persisted nominative registry.

No LICENSE is introduced merely because the repository is temporarily public. Licensing remains a separate future decision if external reuse of Analytics is intentionally offered.

## Final automated validation

The first public-repository workflow execution completed successfully on 2026-09-06:

```text
run #20
id 34026249039
head 7645025c556ea2dd416473268a7019383a6380c2
conclusion success
```

The run validated the full retained pipeline, including:

```text
public-safe participation collection
traffic normalization and rollups
community stock comparison
development activity context
issue / PR lifecycle
curated event projection
M3f ecosystem-context projection
dataset persistence
dashboard-site assembly and persistence
```

The generated `analytics/dashboard_data.json` contains `ecosystem_context` with complete aligned-window coverage for development, lifecycle and participation evidence.

The deployment branch was refreshed successfully by automation:

```text
dashboard-site
commit 593c9e6532a2ffc7827721480583f5e478be48ee
message dashboard: refresh static site
```

The deployed branch also contains the `Ecosystem Context / Community & engineering` presentation section and the generated M3f payload.

The previous non-blocking M3f automation/deployment validation debt is therefore resolved.

## Final presentation acceptance

Desktop and mobile visual acceptance were both completed on 2026-09-06 against the deployed M3f dashboard.

The accepted presentation shows:

```text
Ecosystem pulse populated
traffic charts rendered
curated event context rendered
Community & engineering section populated
community / lifecycle / participation / development summary cards rendered
repository-level context table populated
repository comparison rendered
signal-shape chart rendered
no fatal dashboard-data error
no visible desktop layout breakage
mobile layout usable without blocking overflow or presentation defects
```

The Operational Milestone 1 presentation gate is therefore closed.

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
