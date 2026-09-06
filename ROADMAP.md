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

The final M3f workflow/deployment/visual validation remains explicit TODO work until the first public-repository run is available. It is not represented as already successful. If that run reveals a defect, reopen M3f only.

## Public repository decision

**Status: accepted; visibility switch pending in GitHub settings**

OrbitFabric Analytics is intentionally becoming a public open-source observability project rather than remaining a private internal repository.

Decision principles:

- [x] Public analytics is treated as a project decision, not only as an Actions quota workaround.
- [x] Source, metric semantics, aggregate datasets, reports and dashboard architecture are suitable for public review.
- [x] GitHub Actions secrets remain outside repository content.
- [x] No token-like credential strings found in the current source audit.
- [x] Nominative participant state removed from retained analytics.
- [x] `analytics/community_participants.json` removed from the `github-repo-stats` branch.
- [x] Participation `first_seen` semantics redesigned to reconstruct from public GitHub events since a fixed observation baseline.
- [x] Workflow switched to the public-safe participation collector and no longer persists raw actor identities.
- [ ] Repository visibility changed from private to public in GitHub settings.
- [ ] First public Actions run validates M3f projection, dashboard-site deployment and desktop/mobile rendering.

The historical deleted actor-registry blob contains only the maintainer login `FAROTECH`; no third-party participant identity was ever retained before the public transition.

## M0 - Data Retention

**Status: complete**

- [x] Central analytics repository created.
- [x] Authoritative repository inventory defined.
- [x] Per-repository collection enable/disable policy defined.
- [x] Separate inclusion policy for official ecosystem rollups defined.
- [x] Dynamic GitHub Actions matrix generated from repository configuration.
- [x] Daily `github-repo-stats` collector configured.
- [x] First successful collection run completed.
- [x] `github-repo-stats` data branch verified.

## M1 - Ecosystem Dashboard

**Status: complete**

- [x] Repository-day normalization and official rollups implemented and validated.
- [x] Repository comparison implemented over a common recent window.
- [x] Awareness, technical-evaluation and adoption-proxy boundaries defined without a scalar score.
- [x] Responsive static PWA implemented.
- [x] Cloudflare Pages deployment through `dashboard-site` operational.
- [x] Public-unlisted dashboard policy and anti-indexing controls configured.
- [x] Overview and repository snapshot deltas implemented.
- [x] Repository-scoped unique metrics kept separate from user-identity semantics.
- [x] Desktop and mobile PWA validation completed for the pre-M3f baseline.

## M2 - Event Correlation

**Status: complete**

- [x] Authoritative event registry and taxonomy implemented.
- [x] Repository-aware scope validation implemented.
- [x] Normalized events projected into `dashboard_data.json`.
- [x] Mobile-first event rail and on-demand traffic-chart guide implemented.
- [x] First real traffic/event correlation review completed.
- [x] `community-contribution` added for relevant maintainer technical presence that is not direct OrbitFabric outreach.

Event context remains correlation evidence only. Releases, direct outreach, upstream discussions, community contributions and internal milestones retain distinct meanings.

## M3 - Community Signals

**Status: complete for Operational Milestone 1 scope**

### M3a - Stock snapshot baseline

**Status: complete**

- [x] Daily repository-scoped stock contract defined.
- [x] Stars, forks, open issues, open pull requests and repository-scoped contributor records retained.
- [x] Stock semantics explicitly separated from event-count semantics.

### M3b - Stock deltas

**Status: complete**

- [x] Latest-vs-previous-available snapshot semantics defined.
- [x] Absolute-only stock deltas implemented.
- [x] Snapshot gaps explicit.

### M3c - Development activity context

**Status: complete**

- [x] Rolling 21-day recollection implemented.
- [x] Default-branch commit and GitHub Actions activity retained.
- [x] First-party / automation / other commit classification policy defined.
- [x] Initial clone-spike review completed.

Development activity is explanatory context, not traffic attribution.

### M3d - Issue / pull-request lifecycle

**Status: complete**

- [x] Lifecycle events separated from stock deltas.
- [x] Issue open / close and PR open / merge / close-unmerged semantics implemented.
- [x] Merge-generated close events prevented from becoming false close-unmerged events.
- [x] Initial lifecycle evidence review completed.

### M3e - Repository participation baseline

**Status: complete; public-safe persistence model adopted**

- [x] Participant identity semantics kept repository-scoped rather than ecosystem-wide.
- [x] Rolling 21-day retained output implemented.
- [x] Issue authors, PR authors and issue / PR conversation comments selected as actor-bearing surfaces.
- [x] Daily participant observations classified as first-party / automation / other.
- [x] `other` explicitly kept separate from external-contributor semantics.
- [x] Fixed observation baseline defined at `2026-08-17`.
- [x] First-observed semantics reconstructed from public events without retained raw actor identities.
- [x] `analytics/community_participation_public.py` wired into the workflow.
- [x] Nominative actor registry removed from retained public analytics state.
- [x] Initial participation review completed.

The first retained participation window contains only first-party actors on the currently collected GitHub surfaces. This is a useful T0 baseline, not evidence that nobody external is aware of OrbitFabric.

### M3f - Ecosystem dashboard context

**Status: complete for milestone scope; final operational validation deferred**

- [x] `analytics/dashboard_ecosystem_context.py` added as a downstream presentation projection.
- [x] Community stock retains its own observation date.
- [x] Lifecycle, participation and development context aligned to the traffic comparison window.
- [x] Coverage semantics retained for aligned context families.
- [x] Repository-level community and engineering context projected.
- [x] Participant window totals labelled as repository-day observations rather than deduplicated people.
- [x] `Ecosystem Context / Community & engineering` dashboard section implemented.
- [x] Mobile-responsive summary cards and repository context table implemented.
- [x] Workflow projection step wired after curated-event projection.
- [ ] First M3f projection run validated end to end.
- [ ] First M3f `dashboard-site` deployment and desktop/mobile visual check.

## Deferred TODO after Operational Milestone 1

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
- Participation `first_seen` means earliest reconstructed observation since the configured repository observation baseline.
- `other` participation does not automatically mean an external user or contributor.
- Development activity is contextual evidence, not attribution.
- Curated event proximity is correlation evidence, not causality.
