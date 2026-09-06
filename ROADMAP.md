# OrbitFabric Analytics Roadmap

OrbitFabric Analytics grows in stages. The first priority is preserving trustworthy evidence. Higher-level interpretation comes only after collection and semantic boundaries are stable.

## Operational Milestone 1 - Ecosystem Observability Baseline

**Status: complete**

Goal: establish a durable first analytics baseline that can be left running while OrbitFabric development and outreach continue independently.

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
- [x] First public-repository M3f workflow run completed successfully.
- [x] `ecosystem_context` confirmed in generated `dashboard_data.json`.
- [x] `dashboard-site` refreshed successfully by automation.
- [x] Final desktop presentation check.
- [x] Final mobile presentation check.

The previous M3f validation debt caused by the private-repository Actions quota is resolved. The deployed dashboard has passed both desktop and mobile human visual inspection.

## Repository visibility and public-safe evidence boundary

**Status: accepted and operational**

The durable project decision is that retained Analytics state is **public-safe by design**. Repository visibility may therefore be changed between public and private for operational reasons without changing metric semantics or data-retention boundaries.

The current public period was also used to validate the public-safe design and to execute GitHub-hosted Actions without consuming private-repository minutes. It is not treated as a permanent commitment that this repository must remain public.

Decision principles:

- [x] Source, metric semantics, aggregate datasets, reports and dashboard architecture are safe for public review.
- [x] GitHub Actions secrets remain outside repository content.
- [x] No token-like credential strings were found in the source audit.
- [x] Nominative participant state removed from retained analytics.
- [x] `analytics/community_participants.json` removed from the `github-repo-stats` branch before publication.
- [x] Participation `first_seen` semantics redesigned to reconstruct from public GitHub events since a fixed observation baseline.
- [x] Workflow switched to the public-safe participation collector and no longer persists raw actor identities.
- [x] Repository visibility changed to public for the validation period.
- [x] First public Actions run completed successfully.
- [x] No LICENSE is introduced merely because of the temporary public visibility; licensing remains a separate future decision if external reuse is intentionally offered.

The historical deleted actor-registry blob contained only the maintainer login `FAROTECH`; no third-party participant identity was retained before the public transition.

If repository visibility is later returned to private, the public-safe evidence boundary remains in force so that a future public interval never requires another privacy migration.

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
- [x] Public-safe collector validated in the first public workflow run.
- [x] Initial participation review completed.

The first retained participation window contains only first-party actors on the currently collected GitHub surfaces. This is a useful T0 baseline, not evidence that nobody external is aware of OrbitFabric.

### M3f - Ecosystem dashboard context

**Status: complete and accepted**

- [x] `analytics/dashboard_ecosystem_context.py` added as a downstream presentation projection.
- [x] Community stock retains its own observation date.
- [x] Lifecycle, participation and development context aligned to the traffic comparison window.
- [x] Coverage semantics retained for aligned context families.
- [x] Repository-level community and engineering context projected.
- [x] Participant window totals labelled as repository-day observations rather than deduplicated people.
- [x] `Ecosystem Context / Community & engineering` dashboard section implemented.
- [x] Mobile-responsive summary cards and repository context table implemented.
- [x] Workflow projection step wired after curated-event projection.
- [x] First M3f projection run validated end to end in public run #20.
- [x] Generated `dashboard_data.json` confirmed to contain `ecosystem_context` with complete aligned-window coverage.
- [x] `dashboard-site` refreshed successfully by run #20.
- [x] Desktop visual acceptance completed on the deployed M3f dashboard.
- [x] Mobile visual acceptance completed on the deployed M3f dashboard.

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
