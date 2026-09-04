# OrbitFabric Analytics Roadmap

OrbitFabric Analytics grows in stages. The first priority is preserving data. Higher-level interpretation comes only after the collection baseline is stable.

## M0 - Data Retention

**Status: in progress**

Goal: stop losing GitHub traffic history.

- [x] Central analytics repository created.
- [x] Authoritative repository inventory defined.
- [x] Per-repository collection enable/disable policy defined.
- [x] Separate inclusion policy for future ecosystem rollups defined.
- [x] Dynamic GitHub Actions matrix generated from repository configuration.
- [x] Daily `github-repo-stats` collector configured.
- [ ] `GHRS_GITHUB_API_TOKEN` repository secret configured.
- [ ] First successful collection run completed.
- [ ] `github-repo-stats` data branch verified.

## M1 - Ecosystem Dashboard

**Status: planned**

Goal: turn retained traffic data into a coherent OrbitFabric ecosystem view.

Planned capabilities:

- cross-repository aggregation;
- Core vs Studio vs adapters comparison;
- awareness metrics;
- evaluation signals;
- adoption proxies;
- category-level rollups driven by `include_in_rollups`.

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
