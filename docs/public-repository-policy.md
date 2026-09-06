# Repository visibility and public-safe evidence policy

Status: accepted on 2026-09-06.

## Decision

`FAROTECH/orbitfabric-analytics` retains **public-safe evidence by design**.

Repository visibility is an operational choice and may change between public and private without changing the analytics data contract. The project must therefore remain safe to expose even when a public interval is used for validation, collaboration or GitHub Actions execution.

The public interval used during Operational Milestone 1 is not a permanent commitment that the repository must remain public.

## Public-safe evidence boundary

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

This boundary remains in force even while the repository is private. That keeps future public intervals reversible without another data migration.

## Participation decision

The original M3e implementation used a cumulative repository-scoped actor registry to preserve `first_seen` semantics.

Before the first public interval, that retained registry was removed. At the time of removal it contained only the maintainer login `FAROTECH`; no third-party identity had been retained.

The current design uses:

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

The observation baseline is configured in:

```text
config/community-participation.yml
```

A private persistent participant registry may be reconsidered later only if event reconstruction becomes materially inefficient and repository visibility is intentionally kept private. It is not required for the current milestone or current analytics semantics.

## Branch policy

When the repository is public, all branches must be assumed public.

When the repository is private, branches may be access-controlled by GitHub, but Analytics still applies the same public-safe retention policy:

```text
main
    source, policy, reports and dashboard source

github-repo-stats
    public-safe retained evidence and generated analytics

dashboard-site
    public-safe deployable dashboard artifact
```

Repository privacy is therefore not relied upon as the sole protection for retained analytics data.

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

The Cloudflare Pages dashboard remains public but intentionally unlisted, with anti-indexing controls. `noindex` is a discoverability control, not authentication.

## Licensing

Repository visibility does not by itself imply an open-source license grant.

No LICENSE is introduced merely because the repository is temporarily public. Licensing remains a separate future decision if external reuse or redistribution of Analytics is intentionally offered.

## Future changes

Any future analytics feature that introduces identity-bearing or otherwise sensitive retained state must define its exposure boundary before implementation.
