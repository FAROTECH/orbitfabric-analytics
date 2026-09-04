# OrbitFabric Analytics

Analytics and ecosystem traction monitoring for OrbitFabric projects.

## Purpose

OrbitFabric Analytics preserves and analyzes ecosystem traction signals that are otherwise difficult to retain over time.

The first objective is simple: collect GitHub repository traffic every day so that the history is not lost after GitHub's short traffic-retention window.

The project is intentionally structured so that collection, configuration, analysis and reporting can evolve independently.

## Current status

**M0 - Data Retention: in progress**

The initial baseline provides:

- centralized multi-repository traffic collection;
- repository enable/disable policy in `config/repositories.yml`;
- separation between collected repositories and repositories included in ecosystem rollups;
- daily historical snapshots through `github-repo-stats`;
- a lightweight event registry for future traffic/event correlation.

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
(raw snapshots + generated reports)
        |
        v
future OrbitFabric aggregation / dashboards
```

`main` contains configuration, tooling and documentation.

The generated traffic history and reports are stored separately in the `github-repo-stats` branch.

## Repository policy

Each repository has two independent switches:

```yaml
collect: true
include_in_rollups: true
```

`collect` controls whether daily traffic data is fetched and retained.

`include_in_rollups` controls whether the repository contributes to future aggregate OrbitFabric ecosystem KPIs.

This allows a repository to be monitored without affecting official ecosystem rollups.

## Collector

M0 uses [`jgehrcke/github-repo-stats`](https://github.com/jgehrcke/github-repo-stats), pinned to `v1.4.2`.

The workflow runs once per day and can also be started manually from GitHub Actions.

## Required secret

The collector needs one repository secret:

```text
GHRS_GITHUB_API_TOKEN
```

The token must be able to read traffic statistics for every repository with `collect: true` and push the generated data back to this private repository.

For the initial setup, use a GitHub personal access token belonging to an account with access to all monitored FAROTECH repositories. The `github-repo-stats` documentation recommends a token with `repo` scope.

Add it under:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

After the secret is configured, run **Collect GitHub traffic** manually once to establish the first snapshot.

## Configuration

- `config/repositories.yml`: authoritative repository inventory and collection policy.
- `config/events.yml`: project events that may later be correlated with traffic changes.
- `tools/build_repository_matrix.py`: validates the repository configuration and emits the GitHub Actions matrix.

## Roadmap

See [ROADMAP.md](ROADMAP.md).
