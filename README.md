# OrbitFabric Analytics

Public analytics and ecosystem observability for OrbitFabric projects.

## Purpose

OrbitFabric Analytics preserves and interprets ecosystem evidence that is otherwise difficult to retain over time.

The project separates collection, configuration, analysis and reporting so evidence can evolve without mixing acquisition logic with interpretation or presentation.

The governing rule is:

```text
policy in configuration, logic in tooling
```

## Visibility policy

OrbitFabric Analytics is intentionally an open-source public project.

This is a project decision, not only a GitHub Actions billing workaround. The public repository makes the evidence model, metric semantics and observability tooling inspectable alongside the rest of the OrbitFabric ecosystem.

Only public-safe retained evidence belongs in repository branches. Participation analytics therefore retains aggregate repository-day counts, not a cumulative nominative actor registry.

## Current status

**Operational Milestone 1 - Ecosystem Observability Baseline: complete**

Completed capability layers:

```text
M0  Data Retention                 complete
M1  Ecosystem Dashboard            complete
M2  Event Correlation              complete
M3a Community stock baseline       complete
M3b Community stock deltas         complete
M3c Development activity context   complete
M3d Issue / PR lifecycle           complete
M3e Repository participation       complete
M3f Ecosystem dashboard context    complete and E2E validated
```

The first public-repository workflow run successfully validated the M3f ecosystem-context projection, dataset persistence and `dashboard-site` refresh. Only final human visual acceptance of the deployed desktop/mobile presentation remains.

Richer engagement features are intentionally deferred after this baseline rather than expanding scope indefinitely.

## Evidence model

OrbitFabric Analytics keeps distinct evidence families distinct:

```text
TRAFFIC
views / clones

COMMUNITY STOCK
stars / forks / open issues / open pull requests / repository-scoped contributor records

LIFECYCLE
issue / pull-request open, close and merge events

PARTICIPATION
repository-scoped aggregate actor-bearing activity

DEVELOPMENT CONTEXT
commits / workflow runs

CURATED CONTEXT
releases / outreach / upstream discussions / community contributions
```

None of these families is treated automatically as a direct count of ecosystem users or as proof of adoption.

## Repository policy

`config/repositories.yml` is the authoritative ecosystem inventory.

Each repository has two independent switches:

```yaml
collect: true
include_in_rollups: true
```

`collect` controls retained traffic collection.

`include_in_rollups` controls participation in official OrbitFabric ecosystem analytics. The current official analytics scope contains six repositories: Core, Studio, Reference Mission and the three published adapters.

## Data and branch model

```text
main
    source code
    configuration
    documentation
    dashboard source

github-repo-stats
    retained traffic history
    generated public-safe analytics datasets

dashboard-site
    deployable static dashboard snapshot
```

The browser never talks directly to GitHub and never receives GitHub credentials.

## Main generated datasets

```text
analytics/ecosystem_daily.csv
analytics/ecosystem_rollups_daily.csv
analytics/repository_comparison_latest.csv

analytics/events_normalized.json

analytics/community_daily.csv
analytics/community_comparison_latest.csv
analytics/development_activity_daily.csv
analytics/community_lifecycle_daily.csv
analytics/community_participation_daily.csv

analytics/dashboard_data.json
```

Raw GitHub actor logins used for participation analysis are not retained. `first_seen` is reconstructed from public GitHub events since the explicit observation baseline configured in `config/community-participation.yml`.

## Dashboard

The presentation layer is a static mobile-friendly PWA deployed through Cloudflare Pages.

It presents:

- ecosystem traffic pulse and daily deltas;
- clone and view timelines;
- curated event correlation with interactive chart guides;
- community stock and stock deltas;
- lifecycle, participation and development context aligned to the traffic comparison window;
- repository-level community and engineering context;
- traffic repository comparison and signal shape.

Community stock may be newer than the latest complete traffic day. That difference is explicit in the dashboard instead of being silently merged into one time boundary.

The dashboard URL remains intentionally unlisted and uses anti-indexing controls. Those controls reduce discoverability but are not treated as security.

See [docs/dashboard-architecture.md](docs/dashboard-architecture.md).

## Semantic boundaries

Important interpretation rules:

- GitHub Traffic unique values are repository-scoped and are not ecosystem-wide unique people.
- Clone activity is technical-access evidence and may contain substantial first-party / automation contamination.
- Stock deltas are state changes, not lifecycle event counts.
- `other` participation means not classified as configured first-party or automation; it does not automatically mean external user or contributor.
- Participation window totals are repository-day observations, not deduplicated people.
- Development activity is contextual evidence, not traffic attribution.
- Curated event proximity is correlation context, not proof of causation.

## Automation

`.github/workflows/collect-github-traffic.yml` runs daily and can also be started manually.

The workflow:

```text
collects traffic
    -> collects community / development / lifecycle / participation evidence
    -> builds traffic normalization and rollups
    -> builds dashboard payload
    -> projects curated events
    -> projects ecosystem context
    -> persists datasets on github-repo-stats
    -> assembles dashboard-site
```

The public-safe participation collector reconstructs repository-scoped first-observed state in memory from the fixed observation baseline and writes only aggregate daily counts.

The first public-repository M3f validation run is recorded as:

```text
run #20
id 34026249039
conclusion success
```

## Secrets

Required baseline secret:

```text
GHRS_GITHUB_API_TOKEN
```

Optional M3-specific secret:

```text
COMMUNITY_GITHUB_TOKEN
```

Secrets remain GitHub Actions configuration and are never written to repository files or generated dashboard payloads.

## Deferred work

The first milestone deliberately postpones richer analytics surfaces such as:

- longer rolling trend semantics beyond the current adjacent snapshots and common comparison window;
- pull-request review participation;
- GitHub Discussions;
- reactions where event timestamps can be retained without reconstructing history from current stock;
- richer contributor / participant analysis;
- web and documentation analytics;
- automated intelligence, anomaly detection and periodic reporting.

These remain tracked in [ROADMAP.md](ROADMAP.md) rather than being required for the initial operational baseline.
