# Metrics model

OrbitFabric Analytics separates raw GitHub signals from higher-level interpretation.

The first M1 dataset is intentionally repository-day based. Each row represents one repository on one calendar day.

## Dimensions

Each normalized row contains:

- `date`
- `repository_id`
- `repository`
- `category`
- `include_in_rollups`

Repository classification and rollup policy come from `config/repositories.yml`.

## Raw traffic metrics

The initial dataset retains the GitHub traffic values produced by `github-repo-stats`:

- `clones_total`
- `clones_unique`
- `views_total`
- `views_unique`

These values are evidence of repository activity. They are not direct measurements of external adoption.

## Important interpretation rules

### Unique values are repository-scoped

`clones_unique` and `views_unique` must not be summed across repositories and presented as unique OrbitFabric users.

The same person, runner, bot or automation can access multiple OrbitFabric repositories on the same day. GitHub does not provide an ecosystem-wide identity that would allow those accesses to be deduplicated.

A rollup may expose the sum of repository-level unique values only if it is explicitly named as such and never described as a true unique-user count.

### Clone traffic is not equivalent to external adoption

Clone traffic may include:

- developers evaluating the project;
- maintainers and local development activity;
- CI and greenfield test environments;
- automated tooling;
- bots and indexers.

A clone spike can therefore be a strong activity signal while still having low confidence as evidence of external adoption.

### Views and clones are different signals

Repository views and repository clones should be interpreted separately. A day with many clones and few or no views may reflect automation or direct Git operations rather than normal browsing and evaluation.

### Correlation is not attribution

Events recorded in `config/events.yml`, such as releases, posts or upstream discussions, may be compared with traffic changes. Temporal coincidence is useful evidence but does not by itself prove that an event caused the change.

## M1 normalization contract

`analytics/aggregate.py` builds `ecosystem_daily.csv` from the per-repository `views_clones_aggregate.csv` files stored on the `github-repo-stats` branch.

The normalized schema is:

```text
date
repository_id
repository
category
include_in_rollups
clones_total
clones_unique
views_total
views_unique
```

The generated dataset is persisted on the `github-repo-stats` branch at:

```text
analytics/ecosystem_daily.csv
```

This keeps generated analytics data separate from code and policy on `main`.

The collection workflow builds the normalized dataset only after all enabled repository collectors have completed successfully. This guarantees that one daily dataset is generated from a coherent post-collection state.

## M1 rollup contract

`analytics/rollup.py` consumes the normalized repository-day dataset and produces the first official cross-repository daily rollups.

Only repositories with both:

```yaml
collect: true
include_in_rollups: true
```

participate in official rollups.

The initial scopes are:

```text
ecosystem
category/core
category/product
category/adapter
```

Repositories collected only for technical or ecosystem monitoring remain available in `ecosystem_daily.csv` but do not affect official rollup values.

The rollup schema is:

```text
date
scope_type
scope_id
repositories_expected
repositories_available
coverage_pct
coverage_complete
clones_total
views_total
clones_unique_repo_sum
views_unique_repo_sum
```

The generated rollup dataset is persisted at:

```text
analytics/ecosystem_rollups_daily.csv
```

### Coverage semantics

Coverage is part of the metric, not an optional annotation.

`repositories_expected` is derived from the current repository policy for the selected scope.

`repositories_available` counts repositories that have a repository-day row for the date. A row containing zero traffic is still available data. Missing data is different from measured zero activity.

`coverage_pct` is:

```text
repositories_available / repositories_expected * 100
```

`coverage_complete` is true only when all repositories expected for that scope are available.

Activity totals on a partially covered day are sums over the repositories that are actually available. They must therefore be interpreted together with coverage and must not be compared blindly with complete days.

A day with zero available repositories may still produce a rollup row with zero totals and `coverage_pct = 0`. The zero totals in that case mean "no available measurements", not "measured zero ecosystem activity".

### Additive activity metrics

These metrics are additive across repositories:

- `clones_total`
- `views_total`

They may be summed for ecosystem and category scopes, subject to the coverage rule above.

### Repository-scoped unique sums

The rollup exposes:

- `clones_unique_repo_sum`
- `views_unique_repo_sum`

These names are intentionally explicit. They are sums of repository-level unique counts and are useful as activity or interest signals, but they are not deduplicated people, devices or ecosystem-wide users.

No dashboard should relabel them as "unique OrbitFabric users".

## M1 repository comparison contract

`analytics/compare.py` builds a recent-window comparison across the repositories included in official rollups.

The comparison window does not end on the newest timestamp merely present in the raw data. It ends on the latest day for which the ecosystem rollup has `coverage_complete = true`. This prevents a partially collected latest day from making one repository appear artificially quieter than another.

The default window is 14 calendar days and is identical for every compared repository.

The generated snapshot is persisted at:

```text
analytics/repository_comparison_latest.csv
```

Each repository row contains:

```text
window_start
window_end
window_days
repository_id
repository
category
days_expected
days_available
coverage_pct
coverage_complete
clones_total
views_total
clones_unique_repo_day_sum
views_unique_repo_day_sum
clone_active_days
view_active_days
clone_only_days
view_only_days
mixed_days
inactive_days
clones_per_repo_day_unique
views_per_repo_day_unique
clone_to_view_ratio
```

### Window coverage

`days_available` counts measured repository-day rows inside the common comparison window.

A measured zero-activity day is still available. A missing day is not counted as inactive.

`coverage_pct` therefore describes the completeness of the comparison window for that repository. Repository totals must be interpreted together with this value.

### Activity shape

Each available repository-day is classified deterministically as one of:

- `clone_only`: clone activity, no view activity;
- `view_only`: view activity, no clone activity;
- `mixed`: both clone and view activity;
- `inactive`: measured zero clone and zero view activity.

These are activity shapes, not attribution labels. In particular, `clone_only` does not mean automation and `mixed` does not mean external adoption.

### Awareness evidence

At M1, repository browsing is the cleanest available awareness signal:

- `views_total`
- `views_unique_repo_day_sum`
- `view_active_days`

Even these values may include maintainers, bots or repeated technical access. They are therefore evidence of repository visibility, not a count of external people.

### Technical evaluation / access evidence

Clone activity is treated as a technical access or evaluation signal:

- `clones_total`
- `clones_unique_repo_day_sum`
- `clone_active_days`

It is deliberately not called adoption. During periods of intense OrbitFabric development, CI, greenfield testing, local work and cross-repository integration can dominate these values.

### Diagnostic ratios

The comparison exposes:

- `clones_per_repo_day_unique`
- `views_per_repo_day_unique`
- `clone_to_view_ratio`

They describe activity shape only. `clone_to_view_ratio` is not a conversion rate because GitHub does not link repository viewers to cloners. Ratios with a zero denominator are left empty rather than represented as infinity.

### Adoption proxy semantics

M1 does not produce a scalar "adoption score".

Clone activity can be shown as a low-confidence adoption-interest proxy only when it remains clearly separated from external-user claims and is presented together with activity shape and coverage.

Stronger evidence of adoption will come from additional signals such as forks, stars, issues, pull requests, contributors, releases and external web traffic. Those signals belong to later roadmap stages.

## Separation of concerns

No inferred adoption score, bot filtering or attribution is applied at the normalization, rollup or repository-comparison stages.

That separation is intentional:

```text
raw collection
    -> normalized repository-day dataset
    -> explicit rollups + coverage
    -> fair repository comparison
    -> contextual interpretation
    -> dashboard
```

The dashboard must be downstream of the metric semantics, not the place where those semantics are invented.
