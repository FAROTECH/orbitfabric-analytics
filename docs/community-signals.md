# Community signals

Status: M3 complete for Operational Milestone 1 scope.

## Goal

M3 complements GitHub traffic with repository-level evidence about public engagement and project activity.

Traffic, community and context remain separate evidence families:

```text
TRAFFIC
views / clones

COMMUNITY
stars / forks / issues / pull requests / participants

DEVELOPMENT CONTEXT
commits / workflow runs

CONTEXT
releases / outreach / upstream discussions / community contributions
```

None of these families is treated as a direct count of ecosystem users.

## M3a stock baseline

The generated stock history is:

```text
analytics/community_daily.csv
```

Stock signals:

```text
stars_total
forks_total
open_issues_total
open_pull_requests_total
contributors_repo_count
```

These are repository-state snapshots, not event counts or ecosystem-wide unique people.

## M3b stock comparison

`analytics/community_compare.py` writes:

```text
analytics/community_comparison_latest.csv
```

The comparison rule is:

```text
latest available snapshot
        vs
previous available snapshot
```

Only absolute deltas are used in this baseline. `snapshot_gap_days` keeps collection gaps explicit.

A stock delta remains a state transition, not an event count.

## M3c development activity context

Development activity is retained separately in:

```text
analytics/development_activity_daily.csv
```

It records repository-day commit and GitHub Actions activity over a rolling recollection window. High first-party or automation activity can make traffic contamination more plausible, but it does not prove that development activity caused GitHub traffic.

See `docs/development-activity.md`.

## M3d issue / pull-request lifecycle

Lifecycle evidence is retained in:

```text
analytics/community_lifecycle_daily.csv
```

Event classes:

```text
issues_opened
issues_closed
prs_opened
prs_merged
prs_closed_unmerged
```

These are derived from GitHub lifecycle timestamps, not inferred from stock changes.

See `docs/community-lifecycle.md`.

## M3e repository participation

The public retained participation dataset is:

```text
analytics/community_participation_daily.csv
```

The first actor-bearing surfaces are issue authors, pull-request authors and issue / pull-request conversation comments.

Daily distinct logins are classified in memory through policy as:

```text
first_party
automation
other
```

`other` is not automatically an external contributor. It only means that the login is not currently configured as first-party or automation.

`participants_first_seen_repo_count` means the earliest reconstructed observation since the configured fixed observation baseline for one login in one repository. It does not mean first GitHub activity ever, ecosystem-wide first participation or a new user.

Raw actor identities are not persisted. The public-safe collector reconstructs first-observed state from public GitHub events and retains aggregate repository-day counts only.

See `docs/community-participation.md`.

## Repository scope

M3 selects repositories where:

```yaml
include_in_rollups: true
```

This keeps the community baseline aligned with the six official repositories used by ecosystem analytics while leaving infrastructure and template repositories outside official community interpretation.

## Collection behavior

The M3 collectors can use:

```text
COMMUNITY_GITHUB_TOKEN
```

when configured. Otherwise they reuse:

```text
GHRS_GITHUB_API_TOKEN
```

For public endpoints, collectors may retry anonymously when the configured fine-grained token does not expose a required read permission.

Collectors fail rather than silently persisting partial repository evidence.

## Deferred after Operational Milestone 1

```text
pull-request review participation
GitHub Discussions
reaction events
richer contributor / participant analysis
```

Reactions in particular must not be reconstructed as historical events merely from current reaction counts attached to older objects.
