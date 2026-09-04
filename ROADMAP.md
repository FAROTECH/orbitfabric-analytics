# OrbitFabric Analytics Roadmap

OrbitFabric Analytics grows in stages. The first priority is preserving data. Higher-level interpretation comes only after the collection baseline is stable.

## M0 - Data Retention

**Status: complete**

Goal: stop losing GitHub traffic history.

- [x] Central analytics repository created.
- [x] Authoritative repository inventory defined.
- [x] Per-repository collection enable/disable policy defined.
- [x] Separate inclusion policy for future ecosystem rollups defined.
- [x] Dynamic GitHub Actions matrix generated from repository configuration.
- [x] Daily `github-repo-stats` collector configured.
- [x] `GHRS_GITHUB_API_TOKEN` repository secret configured.
- [x] First successful collection run completed.
- [x] `github-repo-stats` data branch verified.

M0 was validated with a successful end-to-end collection across all repositories enabled at the time of the first run.

## M1 - Ecosystem Dashboard

**Status: in progress**

Goal: turn retained traffic data into a coherent OrbitFabric ecosystem view.

- [x] Define the normalized repository-day dataset.
- [x] Implement the first cross-repository normalization tool.
- [x] Document metric semantics and non-additive unique-count rules.
- [ ] Automate normalized dataset generation after collection.
- [ ] Define explicit ecosystem and category rollups.
- [ ] Add Core vs Studio vs adapters comparison.
- [ ] Define awareness, evaluation and adoption-proxy views.
- [ ] Build the first ecosystem dashboard.

## M2 - Event Correlation

**Status: planned**

Goal: compare traffic changes with relevant project events.

Planned event types include:

- releases;
- public announcements;
- LinkedIn and Reddit posts;
- upstream project discussions;
- documentation launches;
- major ecosystem milestones.

Correlation will be treated as temporal evidence, not proof of causation.

## M3 - Community Signals

**Status: planned**

Goal: complement traffic with public engagement data.

Planned signals:

- stars;
- forks;
- issues;
- pull requests;
- contributors;
- discussions;
- comments and reactions where useful.

## M4 - Web Analytics

**Status: planned**

Goal: understand traffic across the OrbitFabric website/documentation and GitHub ecosystem.

Planned capabilities:

- privacy-friendly web analytics;
- UTM campaign attribution;
- documentation entry/exit paths;
- GitHub and website traffic comparison.

## M5 - Intelligence

**Status: planned**

Goal: surface useful signals automatically without turning metrics into vanity scores.

Potential capabilities:

- weekly trend summaries;
- anomaly detection;
- repository momentum indicators;
- release/outreach impact windows;
- automated ecosystem reports.
