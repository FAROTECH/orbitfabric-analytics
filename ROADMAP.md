# OrbitFabric Analytics Roadmap

OrbitFabric Analytics grows in stages. The first priority is preserving trustworthy evidence. Higher-level interpretation comes only after collection and semantic boundaries are stable.

## Operational Milestone 1 - Ecosystem Observability Baseline

**Status: final validation**

Goal: establish a durable first analytics baseline that can be left running while OrbitFabric development and outreach continue.

Exit criteria:

- [x] Traffic history retained automatically.
- [x] Official ecosystem normalization, rollups and repository comparison operational.
- [x] Static mobile-friendly dashboard deployed.
- [x] Curated event correlation operational.
- [x] Community stock and stock deltas retained.
- [x] Development activity context retained.
- [x] Issue / PR lifecycle retained.
- [x] Repository-scoped participation baseline retained.
- [x] Community and engineering dashboard integration implemented.
- [ ] Final ecosystem-context workflow projection validated end to end.
- [ ] Final dashboard presentation visually validated after M3f deployment.

Richer engagement and intelligence features are deliberately deferred. They are not required to close this first operational milestone.

## M0 - Data Retention

**Status: complete**

Goal: stop losing GitHub traffic history.

- [x] Central analytics repository created.
- [x] Authoritative repository inventory defined.
- [x] Per-repository collection enable/disable policy defined.
- [x] Separate inclusion policy for official ecosystem rollups defined.
- [x] Dynamic GitHub Actions matrix generated from repository configuration.
- [x] Daily `github-repo-stats` collector configured.
- [x] `GHRS_GITHUB_API_TOKEN` repository secret configured.
- [x] First successful collection run completed.
- [x] `github-repo-stats` data branch verified.

## M1 - Ecosystem Dashboard

**Status: complete**

Goal: turn retained traffic data into a coherent OrbitFabric ecosystem view.

- [x] Repository-day normalization contract defined.
- [x] `analytics/aggregate.py` implemented with unit coverage.
- [x] Automated `analytics/ecosystem_daily.csv` generation validated.
- [x] Cross-repository aggregate and coverage semantics defined.
- [x] Ecosystem / core / product / adapter rollups implemented and validated.
- [x] Repository comparison semantics implemented over a common recent window.
- [x] Awareness, technical-evaluation and adoption-proxy boundaries defined without a scalar score.
- [x] `analytics/dashboard_data.py` implemented and validated.
- [x] Responsive static PWA implemented.
- [x] Cloudflare Pages deployment through `dashboard-site` operational.
- [x] Public-unlisted deployment policy and anti-indexing controls configured.
- [x] Overview day-over-day deltas implemented.
- [x] Rolling repository snapshot deltas implemented.
- [x] Repository-scoped unique metrics kept separate from user-identity semantics.
- [x] Desktop and mobile PWA validation completed.

Cloudflare Access remains optional. The Pages URL is technically public but intentionally unlisted; anti-indexing controls are not treated as security.

## M2 - Event Correlation

**Status: complete**

Goal: compare traffic changes with relevant context without turning temporal proximity into causal claims.

- [x] Authoritative event registry retained in `config/events.yml`.
- [x] Event taxonomy separated into `config/event-taxonomy.yml`.
- [x] Stable event contract defined: id, date, type, channel, scope, confidence and label.
- [x] Repository-aware scope validation implemented.
- [x] `analytics/events.py` implemented with unit coverage.
- [x] Normalized event dataset generated automatically.
- [x] Events projected into `dashboard_data.json`.
- [x] Event context rendered alongside traffic.
- [x] Mobile-first event rail and on-demand chart guide implemented.
- [x] First real traffic/event correlation review completed.
- [x] Interactive overlay validated on desktop and mobile.
- [x] `community-contribution` added for relevant maintainer technical presence that is not direct OrbitFabric outreach.

Event context remains correlation evidence only. Releases, direct outreach, upstream discussions, community contributions and internal milestones retain distinct meanings.

## M3 - Community Signals

**Status: finalizing**

Goal: complement traffic and curated events with public repository engagement and project-activity evidence.

### M3a - Stock snapshot baseline

**Status: complete**

- [x] Traffic, community and contextual evidence families explicitly separated.
- [x] Community policy defined in `config/community-signals.yml`.
- [x] Scope aligned with the six official `include_in_rollups: true` repositories.
- [x] Daily repository-scoped stock contract defined.
- [x] Stars, forks, open issues, open pull requests and repository-scoped contributor records retained.
- [x] Stock semantics explicitly separated from event-count semantics.
- [x] `analytics/community.py` implemented with same-day idempotent history merging.
- [x] First automated baseline validated and reviewed.

### M3b - Stock deltas

**Status: complete**

- [x] Latest-vs-previous-available snapshot semantics defined.
- [x] Absolute-only stock deltas implemented.
- [x] Snapshot gaps exposed through `snapshot_gap_days`.
- [x] Missing previous snapshots represented as non-comparable.
- [x] `analytics/community_compare.py` implemented with unit coverage.
- [x] First real cross-date stock comparison validated.

### M3c - Development activity context

**Status: complete**

- [x] Development context kept separate from traffic and community interpretation.
- [x] Policy defined in `config/development-activity.yml`.
- [x] Rolling 21-day recollection implemented.
- [x] Default-branch commit activity retained.
- [x] First-party / automation / other commit classification policy defined.
- [x] GitHub Actions run activity retained.
- [x] `analytics/development_activity.py` implemented and validated.
- [x] Initial clone-spike review completed.

Development activity is explanatory context, not traffic attribution.

### M3d - Issue / pull-request lifecycle

**Status: complete**

- [x] Lifecycle events separated from stock deltas.
- [x] Policy defined in `config/community-lifecycle.yml`.
- [x] Rolling 21-day lifecycle recollection implemented.
- [x] Issue open / close and PR open / merge / close-unmerged semantics defined.
- [x] Pull requests excluded from issue counts despite GitHub API overlap.
- [x] Merge-generated close events prevented from becoming false close-unmerged events.
- [x] `analytics/community_lifecycle.py` implemented and validated.
- [x] Initial lifecycle evidence review completed.

### M3e - Repository participation baseline

**Status: complete**

- [x] Participant identity semantics kept repository-scoped rather than ecosystem-wide.
- [x] Policy defined in `config/community-participation.yml`.
- [x] Rolling 21-day participation recollection implemented.
- [x] Issue authors, PR authors and issue / PR conversation comments selected as initial actor-bearing surfaces.
- [x] Daily participant observations classified as first-party / automation / other.
- [x] `other` explicitly kept separate from external-contributor semantics.
- [x] Repository-scoped first-observed semantics defined.
- [x] Private cumulative actor registry retained in `analytics/community_participants.json`.
- [x] Raw actor registry excluded from dashboard publication.
- [x] `analytics/community_participation.py` implemented and validated.
- [x] Initial participation review completed.

The first retained participation window contains only first-party actors on the currently collected GitHub surfaces. This is a useful T0 baseline, not evidence that nobody external is aware of OrbitFabric.

### M3f - Ecosystem dashboard context

**Status: implementation complete, validation pending**

Goal: turn the dashboard from a traffic-focused surface into the first coherent ecosystem observability surface.

- [x] `analytics/dashboard_ecosystem_context.py` added as a downstream presentation projection.
- [x] Community stock projected without forcing it onto the traffic date boundary.
- [x] Stock snapshot date exposed independently from latest complete traffic day.
- [x] Lifecycle context aggregated over the traffic comparison window.
- [x] Participation context aggregated over the traffic comparison window.
- [x] Development context aggregated over the traffic comparison window.
- [x] Coverage semantics retained for all aligned context families.
- [x] Repository-level community and engineering context projected.
- [x] Participant window totals labelled as repository-day observations rather than deduplicated people.
- [x] Raw participant registry remains private and outside `dashboard_data.json`.
- [x] `Ecosystem Context / Community & engineering` dashboard section implemented.
- [x] Mobile-responsive summary cards and repository context table implemented.
- [x] PWA cache advanced to include M3f assets.
- [x] Dashboard runtime and architecture documentation refreshed.
- [ ] First automated M3f projection into `dashboard_data.json` validated end to end.
- [ ] First M3f `dashboard-site` deployment validated.
- [ ] Final desktop/mobile visual validation completed.

## Deferred TODO after Operational Milestone 1

These features are intentionally postponed until real ecosystem activity makes them worth the added complexity:

- [ ] Rolling trend semantics beyond adjacent snapshots and the current common comparison window.
- [ ] Pull-request review participation signals.
- [ ] GitHub Discussions signals.
- [ ] Reactions only where reliable event timestamps can be retained without reconstructing history from current stock.
- [ ] Richer contributor / participant analysis if repository activity becomes multi-actor enough to justify it.
- [ ] More explicit cross-reading / derived interpretation between traffic, community, lifecycle, participation, development context and curated events.

They remain valid future work, but none blocks the first operational analytics baseline.

## M4 - Web Analytics

**Status: deferred / planned**

Goal: understand traffic across OrbitFabric website/documentation and GitHub.

TODO:

- [ ] Privacy-friendly web analytics.
- [ ] UTM campaign attribution.
- [ ] Documentation entry / exit paths.
- [ ] GitHub and website traffic comparison.

## M5 - Intelligence

**Status: deferred / planned**

Goal: surface useful signals automatically without turning metrics into vanity scores.

TODO:

- [ ] Weekly trend summaries.
- [ ] Anomaly detection.
- [ ] Repository momentum indicators with explicit semantics.
- [ ] Release / outreach impact windows.
- [ ] Automated ecosystem reports.

## Interpretation rules retained across milestones

- GitHub traffic unique metrics are repository-scoped, not ecosystem-wide people.
- Clone activity is technical-access evidence and may contain substantial first-party / automation contamination.
- A stock delta is a state transition, not a lifecycle event count.
- Lifecycle counts are events, not people.
- Participation `first_seen` means first observation retained by Analytics for one login in one repository.
- `other` participation does not automatically mean an external user or contributor.
- Development activity is contextual evidence, not attribution.
- Curated event proximity is correlation evidence, not causality.
