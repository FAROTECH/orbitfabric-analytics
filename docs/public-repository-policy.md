# Public repository policy

Status: accepted on 2026-09-06.

## Decision

`FAROTECH/orbitfabric-analytics` is an intentionally public OrbitFabric project.

The decision is architectural, not merely operational. Analytics is part of the open ecosystem and its collection model, metric semantics, interpretation boundaries and dashboard tooling are intended to be inspectable.

## Public evidence boundary

The repository may retain:

```text
traffic aggregates and history
community stock and stock deltas
issue / PR lifecycle counts
aggregate repository participation counts
development activity context
curated public event context
reports and dashboard presentation data
```

The repository must not retain:

```text
GitHub credentials
private tokens
raw nominative participant registries
confidential OrbitFabric information
private third-party data
```

## Participation decision

The original M3e implementation used a cumulative repository-scoped actor registry to preserve `first_seen` semantics.

Before public publication, that retained registry was removed. At the time of removal it contained only the maintainer login `FAROTECH`; no third-party identity had been retained.

The public-safe design now uses:

```text
fixed observation baseline
        +
public GitHub actor-bearing events
        ↓
in-memory reconstruction of earliest repository observation
        ↓
aggregate repository-day participation metrics
```

No raw login registry is persisted.

The current observation baseline is configured in:

```text
config/community-participation.yml
```

## Branch policy

All branches of a public repository must be assumed public.

```text
main
    public source, policy, reports and dashboard source

github-repo-stats
    public-safe retained evidence and generated analytics

dashboard-site
    public-safe deployable dashboard artifact
```

No branch is treated as a confidentiality boundary.

## Secrets boundary

GitHub Actions secrets remain outside repository contents.

Source code may refer to secret names such as:

```text
GHRS_GITHUB_API_TOKEN
COMMUNITY_GITHUB_TOKEN
```

but secret values must never be written to source, datasets, logs intentionally produced by the project, dashboard payloads or deployment artifacts.

## Dashboard visibility

Repository visibility and dashboard discoverability are separate decisions.

The repository is public by project policy. The Cloudflare Pages dashboard remains public but intentionally unlisted, with anti-indexing controls. `noindex` is a discoverability control, not authentication.

## Future changes

Any future analytics feature that introduces identity-bearing or otherwise sensitive retained state must define its public-data boundary before implementation.
