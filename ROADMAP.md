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

Current baseline:

- [x] Repository-day normalization contract defined.
- [x] `analytics/aggregate.py` implemented.
- [x] Normalization unit test added.
- [x] Post-collection generation of `analytics/ecosystem_daily.csv` configured.
- [x] First automated `ecosystem_daily.csv` generation validated end to end.
- [x] Cross-repository aggregate metric semantics defined.
- [x] Coverage semantics defined for incomplete daily windows.
- [x] Ecosystem / core / product / adapter rollup scopes defined.
- [x] `analytics/rollup.py` implemented with unit coverage.
- [x] Post-collection generation of `analytics/ecosystem_rollups_daily.csv` configured.
- [ ] First automated `ecosystem_rollups_daily.csv` generation validated end to end.
- [ ] Repository comparison view semantics defined.
- [ ] Awareness and evaluation metrics defined.
- [ ] Adoption proxy semantics defined.
- [ ] First ecosystem dashboard generated.

Repository-level unique values will not be treated as ecosystem-wide unique users. Rollups expose only explicitly named sums of repository-scoped unique values.

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
