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

A future rollup may expose the sum of repository-level unique values only if it is explicitly named as such and never described as a true unique-user count.

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

No inferred adoption score, bot filtering or attribution is applied at this stage.

That separation is intentional:

```text
raw collection
    -> normalized repository-day dataset
    -> explicit aggregation rules
    -> contextual interpretation
    -> dashboard
```

The dashboard must be downstream of the metric semantics, not the place where those semantics are invented.
