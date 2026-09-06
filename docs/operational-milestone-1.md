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

Participation retains aggregate repository-day evidence only. Raw actor logins are used transiently during collection and are not persisted into public analytics state.

## Public repository decision

OrbitFabric Analytics is intentionally being published as a public open-source project.

This is part of the project architecture: the analytics code, metric semantics, aggregate evidence and reports are intended to be inspectable. The repository must therefore retain only evidence that is acceptable to expose publicly.

Before the visibility change, the previous cumulative participant registry was removed from `github-repo-stats`. Its historical content contained only the maintainer login `FAROTECH`; no third-party identity had been retained.

Repository-scoped `first_seen` semantics are now reconstructed from public GitHub events since the fixed observation baseline rather than from a persisted nominative registry.

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

## Closure decision

The milestone is accepted as complete on 2026-09-06.

The decision is based on:

- collection and retained data branches operational;
- traffic, event, community, lifecycle, participation and development collectors validated end to end through M3e;
- semantic interpretation boundaries documented;
- dashboard M3f source and payload projection implemented;
- M3f workflow wiring and unit-test coverage present and statically reviewed against the validated dataset contracts;
- PWA deployment architecture already operational and mobile-capable from the previously validated dashboard baseline.

The final M3f GitHub Actions execution could not be performed while the repository was private because the GitHub Free Actions quota was exhausted. This remains a **non-blocking operational validation debt**, not a silently claimed successful run.

## Deferred operational validation

After the repository visibility is switched to public, the first available workflow execution must:

```text
1. execute the workflow containing the M3f ecosystem-context projection
2. confirm dashboard_data.json contains ecosystem_context
3. confirm dashboard-site deployment
4. perform one desktop/mobile visual check
```

If that execution reveals a defect, reopen M3f only. The already validated M0-M3e baseline and this milestone closure are not retroactively invalidated.
