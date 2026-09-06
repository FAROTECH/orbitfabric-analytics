# Community lifecycle signals

Status: M3d in progress.

## Goal

M3d adds event-oriented GitHub community evidence so lifecycle activity is not inferred from changes in stock values.

For example:

```text
open_issues_total: 3 -> 4
```

is only a stock change. It does not prove that exactly one issue was opened. Several issues may have been opened and closed between snapshots.

M3d therefore records lifecycle timestamps directly.

## Dataset

The generated history is:

```text
analytics/community_lifecycle_daily.csv
```

on the `github-repo-stats` branch.

The repository-day key is:

```text
date + repository_id
```

The current policy recollects a rolling 21-day window and replaces overlapping repository-day rows. This allows recent lifecycle history to settle if GitHub state changes while keeping the retained dataset idempotent.

## Signals

```text
issues_opened
issues_closed
prs_opened
prs_merged
prs_closed_unmerged
```

These are event counts derived from GitHub timestamps, not from stock deltas.

An issue opened and closed on the same UTC day contributes to both `issues_opened` and `issues_closed`.

A pull request opened and merged on the same UTC day contributes to both `prs_opened` and `prs_merged`.

A merged pull request is never counted as `prs_closed_unmerged`.

## Repository scope

M3d follows the official ecosystem selection:

```yaml
include_in_rollups: true
```

so the initial lifecycle dataset covers the same six repositories used by the M3 stock baseline and development context.

## Time semantics

The logical collection date determines the inclusive end of the rolling recollection window.

Lifecycle events themselves are grouped by the UTC date of their GitHub timestamp (`created_at`, `closed_at` or `merged_at`). This keeps event-day semantics aligned with the other GitHub activity datasets and avoids assigning events from timestamp-free stock changes.

## GitHub API behavior

The issues endpoint includes pull requests, so M3d explicitly excludes records containing GitHub's `pull_request` marker before counting issue events.

Pull-request events are collected from the pull-request endpoint, where `created_at`, `closed_at` and `merged_at` are available directly.

The collector may use `COMMUNITY_GITHUB_TOKEN`; otherwise it reuses `GHRS_GITHUB_API_TOKEN`. Public endpoint requests retain the existing anonymous fallback behavior when a fine-grained token cannot read a public surface.

## Interpretation boundary

M3d counts lifecycle events, not people.

A daily value such as:

```text
prs_merged = 3
```

means three merge events were observed for that repository and UTC day. It does not mean three contributors, three users or three external participants.

Actor-oriented participation and contributor-arrival semantics remain separate later M3 work.
