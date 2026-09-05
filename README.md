# OrbitFabric Analytics

Analytics and ecosystem traction monitoring for OrbitFabric projects.

## Purpose

OrbitFabric Analytics preserves and interprets ecosystem traction signals that are otherwise difficult to retain over time.

The project separates collection, configuration, analysis and reporting so that evidence can evolve without mixing acquisition logic with interpretation or presentation.

## Current status

**M0 - Data Retention: complete**

The baseline preserves GitHub traffic history across the configured OrbitFabric repositories.

**M1 - Ecosystem Dashboard: complete**

The current dashboard provides:

- repository-day normalization;
- ecosystem / core / product / adapter rollups;
- repository comparison over a common recent window;
- explicit coverage semantics;
- daily and rolling snapshot deltas;
- responsive static PWA deployment through Cloudflare Pages;
- public-unlisted deployment with anti-indexing controls;
- validated desktop and mobile usage.

**M2 - Event Correlation: complete**

Curated releases, outreach and upstream discussion events are normalized, projected into the dashboard and inspectable against traffic through a mobile-first interactive event rail.

**M3 - Community Signals: in progress**

M3 now retains a daily repository-scoped GitHub community baseline for the official OrbitFabric repositories and builds absolute latest-vs-previous stock comparisons when a previous snapshot exists.

## Architecture

```text
config/repositories.yml
        |
        v
repository matrix builder
        |
        v
GitHub Actions collector
        |
        v
github-repo-stats branch
(raw history + generated analytics datasets)
        |
        v
analytics semantics
        |
        v
dashboard_data.json
        |
        v
dashboard-site branch
        |
        v
Cloudflare Pages PWA
```

Event correlation adds a contextual input:

```text
config/events.yml
        +
config/event-taxonomy.yml
        |
        v
analytics/events.py
        |
        v
analytics/events_normalized.json
```

M3 community collection adds a second retained evidence stream:

```text
config/community-signals.yml
        +
config/repositories.yml
        |
        v
analytics/community.py
        |
        v
analytics/community_daily.csv
        |
        v
analytics/community_compare.py
        |
        v
analytics/community_comparison_latest.csv
```

`main` contains source code, configuration, documentation and dashboard source.

`github-repo-stats` contains retained history and generated analytics datasets.

`dashboard-site` contains the deployable static dashboard snapshot.

## Repository policy

Each repository has two independent switches:

```yaml
collect: true
include_in_rollups: true
```

`collect` controls whether daily traffic data is fetched and retained.

`include_in_rollups` controls whether the repository contributes to official OrbitFabric ecosystem rollups.

This allows a repository to be monitored without affecting ecosystem KPIs.

The first M3 community baseline intentionally follows `include_in_rollups: true`, so community interpretation starts from the same six official repositories used by ecosystem rollups.

## Event policy

`config/events.yml` is the authoritative event timeline.

`config/event-taxonomy.yml` defines allowed event types, channels and confidence levels.

Events are context markers only. Temporal correlation is not treated automatically as proof that an event caused a traffic change.

Historical events are added only when their date and meaning are known well enough to be useful. Approximate dates are explicitly marked as such.

See [docs/event-correlation.md](docs/event-correlation.md).

## Community signal policy

`config/community-signals.yml` defines M3 community stock policy.

The retained stock signals are:

```text
stars_total
forks_total
open_issues_total
open_pull_requests_total
contributors_repo_count
```

These are repository-state snapshots, not counts of new events and not counts of unique ecosystem users.

M3b compares the latest available snapshot with the previous available snapshot for each repository. It exposes absolute deltas only and records `snapshot_gap_days` explicitly. When no previous snapshot exists, the row is marked non-comparable and delta fields remain empty.

Percentage deltas are intentionally omitted from the initial low-cardinality community baseline.

Event-oriented community activity is introduced separately in later M3 increments.

See [docs/community-signals.md](docs/community-signals.md).

## Collector

Traffic collection uses [`jgehrcke/github-repo-stats`](https://github.com/jgehrcke/github-repo-stats), pinned to `v1.4.2`.

The workflow also executes the M3 community snapshot collector and latest stock comparison after the traffic jobs complete.

The workflow runs once per day and can also be started manually from GitHub Actions.

## Required secret

The traffic collector needs one repository secret:

```text
GHRS_GITHUB_API_TOKEN
```

Use a fine-grained personal access token with access to this analytics repository and to every repository where `collect: true`.

Required repository permissions for the traffic baseline:

```text
Administration: Read-only
Contents: Read and write
```

`Administration: Read-only` is required by GitHub's repository traffic endpoints. `Contents: Read and write` allows `github-repo-stats` to clone this private data repository and push snapshots and generated reports to the data and deployment branches.

For a least-privilege setup, select only `FAROTECH/orbitfabric-analytics` plus the repositories currently enabled for collection. If another repository is enabled later, grant the token access to it as well.

M3 can optionally use a separate secret:

```text
COMMUNITY_GITHUB_TOKEN
```

If it is not configured, the collector reuses `GHRS_GITHUB_API_TOKEN`. Public community endpoints can fall back to anonymous access when the fine-grained token does not expose the required permission. A dedicated least-privilege community token can be introduced later when M3 expands to discussions, comments and reactions.

## Configuration

- `config/repositories.yml`: authoritative repository inventory and collection / rollup policy.
- `config/events.yml`: authoritative event timeline.
- `config/event-taxonomy.yml`: event type, channel and confidence policy.
- `config/community-signals.yml`: M3 community stock and comparison policy.
- `tools/build_repository_matrix.py`: validates repository configuration and emits the GitHub Actions matrix.
- `analytics/events.py`: validates and normalizes event context for M2.
- `analytics/community.py`: collects and retains repository-scoped M3 community snapshots.
- `analytics/community_compare.py`: builds latest-vs-previous absolute stock comparisons.

## Roadmap

See [ROADMAP.md](ROADMAP.md).
