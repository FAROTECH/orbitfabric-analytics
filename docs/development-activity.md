# Development activity context

Status: M3c complete.

## Goal

M3c adds machine-derived development context so GitHub traffic can be read alongside evidence of active first-party engineering and automation.

This is contextual evidence, not attribution. A day with many commits or workflow runs does not prove that development activity caused clone or view traffic.

## Dataset

The generated history is:

```text
analytics/development_activity_daily.csv
```

on the `github-repo-stats` branch.

Rows are keyed by:

```text
date + repository_id
```

and use UTC calendar days so activity timestamps have a stable repository-independent boundary.

## Repository scope

The initial M3c scope follows the same six official repositories selected through:

```yaml
include_in_rollups: true
```

The policy is defined in:

```text
config/development-activity.yml
```

## Initial signals

```text
commits_total
first_party_commits
automation_commits
other_commits
workflow_runs_total
workflow_runs_success
workflow_runs_failure
workflow_runs_other
```

Commit counts describe commits observed on the repository default branch in each UTC day.

Commit classification is policy-driven. The initial first-party identity is `FAROTECH`; configured bot logins are classified as automation. A commit that does not map to either set is recorded as `other_commits`.

`other_commits` must not be interpreted automatically as an external contributor count. GitHub author/committer account mapping can be absent or incomplete, and identity semantics remain repository-scoped.

Workflow-run counts describe GitHub Actions runs created for the default branch. They provide automation intensity context, especially when interpreting large clone volumes that may overlap periods of heavy CI or release activity.

## Historical backfill

M3c recollects a rolling 21-day window on every run. The window is merged idempotently into retained history, replacing matching repository-day rows instead of duplicating them.

This gives immediate development context for the currently retained traffic period rather than waiting several weeks to accumulate a new baseline.

Older rows remain retained after they fall outside the rolling recollection window.

## Interpretation boundary

M3c can support statements such as:

```text
High clone traffic occurred during a day with substantial first-party development and CI activity.
```

It does not support statements such as:

```text
Those workflow runs caused the clone traffic.
```

The intended later dashboard cross-reading is:

```text
TRAFFIC
    +
COMMUNITY
    +
DEVELOPMENT CONTEXT
    +
CURATED EVENTS
```

with each evidence family retaining its own semantics.

The first retained review of the high-clone period is documented in `reports/development-context/2026-09-02-to-04-clone-spikes.md`.
