# Community participation signals

Status: M3e in progress.

## Goal

M3e adds repository-scoped participation evidence on top of stock, lifecycle and development-activity datasets.

The purpose is not to manufacture a global user count. It is to observe whether GitHub activity around an OrbitFabric repository involves only configured first-party identities, automation, or additional participant logins.

## Dataset

The generated daily history is:

```text
analytics/community_participation_daily.csv
```

The private repository-scoped actor registry is:

```text
analytics/community_participants.json
```

Both are retained on the private `github-repo-stats` branch.

The raw actor registry is analytics evidence only. It is not copied into the public-unlisted dashboard deployment. Any future dashboard projection must publish aggregate counts rather than raw actor logins.

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

These counts are derived from the retained actor registry.

`first_seen` means:

```text
earliest observation retained by OrbitFabric Analytics
for this login in this repository
```

It does not mean:

```text
first GitHub activity ever
first participation anywhere in OrbitFabric
new user
new external contributor
```

The initial registry is seeded from the rolling historical backfill. Its `observation_start_date` makes that boundary explicit.

If a later backfill reaches an earlier activity date for an existing login, the registry can move that repository-scoped first observation earlier and the recollected daily window is recalculated accordingly.

## Historical recollection

The initial policy recollects a rolling 21-day window on every run.

Daily rows are merged idempotently using:

```text
date + repository_id
```

The actor registry is cumulative, so a participant first observed before the current 21-day window is not incorrectly rediscovered as new when older daily rows fall out of recollection.

## Relationship to other M3 evidence

The intended separation is:

```text
COMMUNITY STOCK
stars / forks / open issue and PR state

LIFECYCLE
issue and PR open / close / merge events

PARTICIPATION
actor-bearing author and comment events + repository-scoped distinct actors

DEVELOPMENT CONTEXT
commits / workflow runs / first-party engineering intensity
```

These layers can later be cross-read in the dashboard, but their semantics remain independent.

## Deferred surfaces

GitHub Discussions, review participation and reaction events are not folded into this first participation contract automatically.

They require separate API and semantic decisions, especially because reactions are often available as current counts on historical objects rather than as timestamped reaction events.

M3 should add them only when they can be represented without retroactively mislabeling stock as event history.
