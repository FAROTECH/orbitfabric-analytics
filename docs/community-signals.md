# Community signals

Status: M3 in progress.

## Goal

M3 complements GitHub traffic with repository-level evidence about public engagement and project activity.

Traffic, community and context remain separate evidence families:

```text
TRAFFIC
views / clones

COMMUNITY
stars / forks / issues / pull requests / contributors

CONTEXT
releases / outreach / upstream discussions
```

None of these families is treated as a direct count of ecosystem users.

## M3a stock baseline

The first M3 increment records daily GitHub stock snapshots for the repositories that participate in official ecosystem rollups.

The authoritative policy is:

```text
config/community-signals.yml
```

The generated history is:

```text
analytics/community_daily.csv
```

on the `github-repo-stats` branch.

The repository-day key is:

```text
date + repository_id
```

A rerun on the same date replaces that repository snapshot instead of duplicating it.

## Initial signals

```text
stars_total
forks_total
open_issues_total
open_pull_requests_total
contributors_repo_count
```

These are stock metrics. They describe repository state at collection time.

This distinction matters. For example, a change from 10 to 11 open issues does not prove that exactly one issue was created during the interval. Multiple issues may have been opened and closed between snapshots.

Likewise, stars and forks can decrease, and a contributor count is a repository-scoped GitHub contributor-record count rather than an ecosystem-wide count of unique people.

## M3b stock comparison

`analytics/community_compare.py` builds the latest repository comparison from retained stock history and writes:

```text
analytics/community_comparison_latest.csv
```

The comparison rule is intentionally simple:

```text
latest available snapshot
        vs
previous available snapshot
```

For each repository the dataset exposes:

```text
current_date
previous_date
snapshot_gap_days
comparable
<metric current value>
<metric absolute delta>
```

Only absolute deltas are used in this increment. Percentage changes are intentionally omitted because the current community baseline is small and percentages would exaggerate low-cardinality changes.

When no previous snapshot exists, `comparable=false` and all delta fields remain empty.

`snapshot_gap_days` makes collection gaps explicit. A delta across a two-day gap is still valid as an observed state change, but it must not be described as a one-day change.

A stock delta remains a state transition, not an event count. For example:

```text
open_issues_total: 4 -> 3
open_issues_total_delta: -1
```

means that the observed open-issue stock decreased by one between snapshots. It does not by itself say how many issues were opened or closed during the interval.

The same caution applies to contributor count. `contributors_repo_count_delta=+1` does not yet mean "one new contributor"; contributor arrival requires an event-oriented identity-aware contract in a later M3 increment.

## Repository scope

M3 currently selects repositories where:

```yaml
include_in_rollups: true
```

This keeps the community baseline aligned with the six official repositories used by ecosystem analytics while leaving infrastructure and template repositories outside official community interpretation.

## Collection behavior

`analytics/community.py` reads repository policy, queries public GitHub REST evidence and merges the current snapshot into `analytics/community_daily.csv`.

The collector can use:

```text
COMMUNITY_GITHUB_TOKEN
```

when a dedicated community token is configured. Otherwise it reuses:

```text
GHRS_GITHUB_API_TOKEN
```

For public endpoints, if a fine-grained token does not carry the permission required by an endpoint, the collector can retry that request anonymously. This is a compatibility fallback, not the long-term preferred permission model.

The collection fails rather than silently persisting a partial repository snapshot.

## What is intentionally deferred

The stock layer does not infer event counts and does not yet collect:

```text
new issues / closed issues
new pull requests / merged pull requests
commit activity
GitHub Discussions
comments
reactions
new contributor events
```

Those signals require event-oriented semantics and, for some GitHub surfaces, additional API permissions. They belong to later M3 increments rather than being mixed into the stock-snapshot contract.

Commit/activity context is specifically planned because it will help distinguish periods dominated by first-party development from periods where external community evidence is increasing.
