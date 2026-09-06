# OrbitFabric Analytics Roadmap

OrbitFabric Analytics grows in stages. The first priority is preserving trustworthy evidence. Higher-level interpretation comes only after collection and semantic boundaries are stable.

## Operational Milestone 1 - Ecosystem Observability Baseline

**Status: complete**

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
- [x] Milestone accepted with explicit non-blocking M3f validation debt after GitHub Actions quota exhaustion.

The final M3f workflow/deployment/visual validation remains a TODO and must be executed at the first available Actions run. It is not represented as already successful. If that future run reveals a defect, reopen M3f only.

Richer engagement and intelligence features are deliberately deferred. They are not required to close this first operational milestone.

## M0 - Data Retention

**Status: complete**

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

- [x] Repository-day normalization contract defined.
- [x] `analytics/aggregate.py` implemented with unit coverage.
- [x] Automated `analytics/ecosystem_daily.csv` generation validated.
- [x] Ecosystem / core / product / adapter rollups implemented and validated.
- [x] Repository comparison implemented over a common recent window.
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

- [x] Authoritative event registry retained in `config/events.yml`.
- [x] Event taxonomy separated into `config/event-taxonomy.yml`.
- [x] Stable event contract defined.
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

**Status: complete for Operational Milestone 1 scope**

Goal: complement traffic and curated events with public repository engagement and project-activity evidence.

### M3a - Stock snapshot baseline

**Status: complete**

- [x] Daily repository-scoped stock contract defined.
- [x] Stars, forks, open issues, open pull requests and repository-scoped contributor records retained.
- [x] Stock semantics explicitly separated from event-count semantics.
- [x] `analytics/community.py` implemented and validated.

### M3b - Stock deltas

**Status: complete**

- [x] Latest-vs-previous-available snapshot semantics defined.
- [x] Absolute-only stock deltas implemented.
- [x] Snapshot gaps exposed through `snapshot_gap_days`.
- [x] Missing previous snapshots represented as non-comparable.
- [x] `analytics/community_compare.py` implemented and validated.

### M3c - Development activity context

**Status: complete**

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
- [x] Rolling 21-day lifecycle recollection implemented.
- [x] Issue open / close and PR open / merge / close-unmerged semantics defined.
- [x] Pull requests excluded from issue counts despite GitHub API overlap.
- [x] Merge-generated close events prevented from becoming false close-unmerged events.
- [x] `analytics/community_lifecycle.py` implemented and validated.
- [x] Initial lifecycle evidence review completed.

### M3e - Repository participation baseline

**Status: complete**

- [x] Participant identity semantics kept repository-scoped rather than ecosystem-wide.
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

**Status: complete for milestone scope; final operational validation deferred**

- [x] `analytics/dashboard_ecosystem_context.py` added as a downstream presentation projection.
- [x] Community stock projected without forcing it onto the traffic date boundary.
- [x] Stock snapshot date exposed independently from latest complete traffic day.
- [x] Lifecycle, participation and development context aligned to the traffic comparison window.
- [x] Coverage semantics retained for aligned context families.
- [x] Repository-level community and engineering context projected.
- [x] Participant window totals labelled as repository-day observations rather than deduplicated people.
- [x] Raw participant registry remains private and outside `dashboard_data.json`.
- [x] `Ecosystem Context / Community & engineering` dashboard section implemented.
- [x] Mobile-responsive summary cards and repository context table implemented.
- [x] PWA cache and dashboard documentation refreshed.
- [x] Workflow projection step wired after curated-event projection.
- [ ] First M3f projection run validated end to end. **Deferred: GitHub Actions quota exhausted.**
- [ ] First M3f `dashboard-site` deployment and desktop/mobile visual check. **Deferred until the first available run.**

These two unchecked items are explicit validation debt, not unimplemented feature scope.

## Deferred TODO after Operational Milestone 1

- [ ] Execute the first available M3f workflow run after GitHub Actions capacity returns; verify `ecosystem_context`, dashboard-site deployment and desktop/mobile rendering.
- [ ] Rolling trend semantics beyond adjacent snapshots and the current common comparison window.
- [ ] Pull-request review participation signals.
- [ ] GitHub Discussions signals.
- [ ] Reactions only where reliable event timestamps can be retained without reconstructing history from current stock.
- [ ] Richer contributor / participant analysis if repository activity becomes multi-actor enough to justify it.
- [ ] More explicit cross-reading / derived interpretation between traffic, community, lifecycle, participation, development context and curated events.

## M4 - Web Analytics

**Status: deferred / planned**

- [ ] Privacy-friendly web analytics.
- [ ] UTM campaign attribution.
- [ ] Documentation entry / exit paths.
- [ ] GitHub and website traffic comparison.

## M5 - Intelligence

**Status: deferred / planned**

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
