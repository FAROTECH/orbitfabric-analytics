# Community lifecycle signals

Status: M3d in progress.

## Goal

M3d adds event-oriented GitHub community evidence so lifecycle activity is not inferred from changes in stock values.

For example:

```text
open_issues_total: 3 -> 4
```

is only a stock change. It does not prove that exactly one issue was opened. Several issues may have been opened and closed between snapshots.

M3d therefore records lifecycle evidence directly.

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

The current policy recollects a rolling 21-day window and replaces overlapping repository-day rows. This allows recent lifecycle history to settle while keeping the retained dataset idempotent.

## Signals

```text
issues_opened
issues_closed
prs_opened
prs_merged
prs_closed_unmerged
```

Open events are derived from the resource `created_at` timestamp. Close and merge counts use GitHub repository issue-event records rather than inferring lifecycle from stock changes or only from the resource's current terminal state.

That distinction matters for close/reopen histories: a historical `closed` event remains observable even if the issue or pull request is later reopened.

An issue opened and closed on the same UTC day contributes to both `issues_opened` and `issues_closed`.

A pull request opened and merged on the same UTC day contributes to both `prs_opened` and `prs_merged`.

GitHub emits a `merged` event followed by a `closed` event for a merged pull request. M3d treats a close event occurring within five seconds of the corresponding merge event as the merge closure and does not also count it as `prs_closed_unmerged`.

A genuine unmerged close followed by a later reopen and merge remains a separate `prs_closed_unmerged` event because it is not temporally paired with the later merge.

## Repository scope

M3d follows the official ecosystem selection:

```yaml
include_in_rollups: true
```

so the initial lifecycle dataset covers the same six repositories used by the M3 stock baseline and development context.

## Time semantics

The logical collection date determines the inclusive end of the rolling recollection window.

Lifecycle evidence is grouped by UTC day. Openings use the resource `created_at` timestamp; closes and merges use the GitHub issue-event `created_at` timestamp. This keeps event-day semantics aligned with the other GitHub activity datasets.

## GitHub API behavior

The issues endpoint includes pull requests, so M3d explicitly excludes records containing GitHub's `pull_request` marker before counting issue openings.

Pull-request openings are read from the pull-request endpoint.

Close and merge activity is read from the repository issue-events endpoint. Repository issue-event records include the referenced issue or pull request, allowing M3d to separate issue closes, pull-request merges and pull-request closes.

The collector may use `COMMUNITY_GITHUB_TOKEN`; otherwise it reuses `GHRS_GITHUB_API_TOKEN`. Public endpoint requests retain the existing anonymous fallback behavior when a fine-grained token cannot read a public surface.

## Interpretation boundary

M3d counts lifecycle events, not people.

A daily value such as:

```text
prs_merged = 3
```

means three merge events were observed for that repository and UTC day. It does not mean three contributors, three users or three external participants.

Actor-oriented participation and contributor-arrival semantics remain separate later M3 work.
