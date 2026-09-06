# Community participation signals

Status: M3e complete.

## Goal

M3e adds repository-scoped participation evidence on top of stock, lifecycle and development-activity datasets.

The purpose is not to manufacture a global user count. It is to observe whether GitHub activity around an OrbitFabric repository involves only configured first-party identities, automation, or additional participant logins.

## Retained dataset

The generated daily history is:

```text
analytics/community_participation_daily.csv
```

It contains aggregate repository-day counts only.

Raw GitHub logins are used transiently while collecting public GitHub events and are not persisted as analytics state.

## Public-repository boundary

OrbitFabric Analytics is designed to be publishable as a public repository.

For participation, the retained boundary is therefore:

```text
public GitHub actor-bearing events
        ↓
in-memory actor reconstruction
        ↓
repository-day aggregate counts
        ↓
public analytics history
```

There is no cumulative nominative participant registry in the retained public data branch.

## Repository scope

M3e follows the same official ecosystem selection:

```yaml
include_in_rollups: true
```

The initial baseline therefore covers the six official OrbitFabric repositories.

## Event surfaces

The first M3e increment observes three actor-bearing GitHub surfaces:

```text
issue_author_events
pr_author_events
comment_events
```

`issue_author_events` counts non-pull-request issues created in the UTC day.

`pr_author_events` counts pull requests created in the UTC day.

`comment_events` counts issue or pull-request conversation comments created in the UTC day.

These are event counts, not participant counts. One actor can create multiple events in the same day.

## Daily distinct participant counts

For every repository and UTC day, logins observed across the enabled event surfaces are deduplicated within that repository-day.

The resulting signals are:

```text
participants_repo_count
first_party_participants_repo_count
automation_participants_repo_count
other_participants_repo_count
```

Classification is policy-driven through `config/community-participation.yml`.

The initial first-party login is `FAROTECH`. Known bot logins are classified as automation. Any remaining login is `other`.

`other` must not be rewritten as `external contributor`. It only means that the observed login is not currently configured as first-party or automation.

Repository-scoped participant counts are not ecosystem-wide unique people. The same login active in two repositories contributes once to each repository's daily participant count.

## First-observed semantics

M3e also records:

```text
participants_first_seen_repo_count
other_participants_first_seen_repo_count
```

`first_seen` means:

```text
earliest reconstructed observation since the configured observation baseline
for this login in this repository
```

The observation boundary is explicit in policy:

```yaml
history:
  observation_start_date: "2026-08-17"
```

It does not mean:

```text
first GitHub activity ever
first participation anywhere in OrbitFabric
new user
new external contributor
```

The public-safe collector reconstructs first-observed state from GitHub events starting at that fixed baseline on every run. This preserves the semantic without retaining a nominative actor registry.

## Historical recollection

The retained daily output still recollects a rolling 21-day window on every run.

Daily rows are merged idempotently using:

```text
date + repository_id
```

The fixed observation baseline can be optimized later if participation volume grows enough to make full reconstruction expensive. That optimization must preserve the same public-data boundary.

## Relationship to other M3 evidence

The intended separation is:

```text
COMMUNITY STOCK
stars / forks / open issue and PR state

LIFECYCLE
issue and PR open / close / merge events

PARTICIPATION
actor-bearing author and comment events + repository-scoped aggregate actor counts

DEVELOPMENT CONTEXT
commits / workflow runs / first-party engineering intensity
```

These layers can be cross-read in the dashboard, but their semantics remain independent.

## Deferred surfaces

GitHub Discussions, review participation and reaction events are intentionally deferred after Operational Milestone 1.

They should be added only when their API and timestamp semantics justify the extra complexity.
