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

**Status: complete**

Goal: turn retained traffic data into a coherent OrbitFabric ecosystem view.

Completed baseline:

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
- [x] First automated `ecosystem_rollups_daily.csv` generation validated end to end.
- [x] Repository comparison view semantics defined.
- [x] Awareness and technical-evaluation metric semantics defined.
- [x] Adoption proxy semantics defined without introducing a scalar adoption score.
- [x] `analytics/compare.py` implemented with unit coverage.
- [x] Post-collection generation of `analytics/repository_comparison_latest.csv` configured.
- [x] First automated `repository_comparison_latest.csv` generation validated end to end.
- [x] Dashboard presentation payload contract defined.
- [x] `analytics/dashboard_data.py` implemented with unit coverage.
- [x] Post-collection generation of `analytics/dashboard_data.json` configured.
- [x] First automated `analytics/dashboard_data.json` generation validated end to end.
- [x] Initial responsive static PWA source implemented under `dashboard/`.
- [x] Cloudflare Pages project configured.
- [x] Public-unlisted deployment policy selected; `noindex` / `robots.txt` controls configured.
- [x] `dashboard-site` deployment branch automation configured.
- [x] First automated `dashboard-site` refresh validated end to end.
- [x] Cloudflare production branch switched to `dashboard-site`.
- [x] First deployed ecosystem dashboard validated on desktop.
- [x] Snapshot delta semantics defined.
- [x] Overview delta implemented as latest complete day vs previous complete day.
- [x] Repository delta implemented as current rolling comparison window vs previous complete snapshot of the same window length.
- [x] Repository-scoped unique deltas kept explicitly separate from user identity semantics.
- [x] Snapshot delta UI implemented for Overview and Repository Comparison.
- [x] First automated snapshot-delta payload and deployment validated end to end.
- [x] PWA / mobile validation completed.

Cloudflare Access is intentionally deferred. It can be introduced later if dashboard confidentiality becomes a requirement. Until then the Pages URL is public but intentionally unlisted; anti-indexing controls reduce discoverability but are not treated as security.

Repository-level unique values will not be treated as ecosystem-wide unique users. Rollups expose only explicitly named sums of repository-scoped unique values. Repository comparisons use a common recent window anchored to the latest complete ecosystem day.

Snapshot deltas are directional activity changes, not quality scores. An increase is not automatically positive and a decrease is not automatically negative. Percentage deltas are omitted when the previous value is zero and the current value is non-zero; that state is represented as `new`.

The dashboard remains downstream of metric semantics and consumes generated presentation data. It does not access GitHub credentials or infer external adoption inside the browser.

## M2 - Event Correlation

**Status: complete**

Goal: compare traffic changes with relevant project events without turning temporal proximity into causal claims.

Completed baseline:

- [x] Authoritative event registry retained in `config/events.yml`.
- [x] Event taxonomy separated into `config/event-taxonomy.yml`.
- [x] Stable event contract defined: id, date, type, channel, scope, confidence and label.
- [x] Repository-aware event scope validation defined.
- [x] `analytics/events.py` implemented to validate and normalize the event registry.
- [x] Event registry unit coverage added.
- [x] Post-collection generation of `analytics/events_normalized.json` configured.
- [x] First automated `analytics/events_normalized.json` generation validated end to end.
- [x] Normalized events projected into `dashboard_data.json`.
- [x] Event context rendered alongside the dashboard activity timeline.
- [x] First automated event-projection payload and deployment validated end to end.
- [x] Mobile-first event rail with on-demand traffic-chart guide implemented.
- [x] Traffic/event overlay implemented for correlation inspection.
- [x] First automated interactive traffic/event overlay deployment validated end to end.
- [x] Initial set of confirmed public OrbitFabric events curated.
- [x] First traffic/event correlation review completed.
- [x] Interactive event overlay visually validated on desktop and mobile.

Planned event classes include releases, outreach, upstream discussions, documentation launches, internal milestones and major ecosystem milestones. Channels are policy-driven and currently include GitHub, LinkedIn, Reddit, Hackaday, Libre Space, website and internal analytics context.

Historical events are not invented merely to populate the dashboard. When a date is uncertain but still useful, it is explicitly marked `approximate`; confirmed day-level correlation uses `confirmed` events.

The event context distinguishes events already inside the retained traffic window from events awaiting a future complete traffic day and events older than the retained timeline. This keeps the dashboard explicit about whether correlation can actually be inspected yet.

The traffic/event overlay is intentionally interaction-driven: the rail is always visible, while a thin guide is drawn across both traffic charts only when an in-window event day is selected. This avoids permanently cluttering the charts and keeps the interaction usable on small screens.

The first correlation review is documented in `reports/correlation/2026-09-04-fprime.md`. It records a real same-day traffic/event correlation around the F´ adapter while explicitly keeping attribution unresolved because release activity and first-party/automation effects are confounding factors.

Correlation will be treated as temporal evidence, not proof of causation.

## M3 - Community Signals

**Status: in progress**

Goal: complement traffic and curated context with public engagement and project-activity evidence.

M3a stock-snapshot baseline:

- [x] Traffic, community and contextual evidence families explicitly separated.
- [x] Community policy defined in `config/community-signals.yml`.
- [x] Initial repository selection aligned with the six official `include_in_rollups: true` repositories.
- [x] Daily repository-scoped stock contract defined.
- [x] Initial stock signals defined: stars, forks, open issues, open pull requests and repository-scoped contributor records.
- [x] Stock metric semantics explicitly separated from event-count semantics.
- [x] `analytics/community.py` implemented with same-day idempotent history merging.
- [x] Community snapshot unit coverage added.
- [x] Post-collection generation of `analytics/community_daily.csv` configured.
- [x] First automated `analytics/community_daily.csv` generation validated end to end.
- [x] Initial community baseline reviewed for all six official repositories.

M3b stock deltas:

- [x] Latest-vs-previous-available snapshot comparison semantics defined.
- [x] Stock deltas kept absolute-only; percentage deltas intentionally excluded from the initial low-cardinality baseline.
- [x] Snapshot gaps exposed explicitly through `snapshot_gap_days`.
- [x] Missing previous snapshots represented as non-comparable rather than synthetic zero deltas.
- [x] `analytics/community_compare.py` implemented with unit coverage.
- [x] Post-collection generation of `analytics/community_comparison_latest.csv` configured.
- [x] First automated `analytics/community_comparison_latest.csv` generation validated end to end.
- [ ] First real comparable stock delta observed from two distinct collection dates.

M3c development activity context:

- [x] Machine-derived development context kept separate from traffic and community interpretation.
- [x] Development activity policy defined in `config/development-activity.yml`.
- [x] Initial scope aligned with the six official repositories.
- [x] Rolling 21-day historical recollection window defined.
- [x] Daily default-branch commit activity contract defined.
- [x] Policy-driven first-party / automation / other commit classification defined.
- [x] Daily GitHub Actions run activity contract defined.
- [x] `analytics/development_activity.py` implemented with idempotent repository-day history merging.
- [x] Development activity unit coverage added.
- [x] Post-collection generation of `analytics/development_activity_daily.csv` configured.
- [ ] First automated development-activity backfill validated end to end.
- [ ] Initial development context reviewed against known high-clone days.

Planned M3 increments:

- [ ] Rolling trend semantics beyond adjacent observed snapshots.
- [ ] Event-oriented issue lifecycle signals.
- [ ] Event-oriented pull-request lifecycle signals.
- [ ] Contributor arrival / participation signals without ecosystem-wide identity assumptions.
- [ ] GitHub Discussions signals.
- [ ] Comments and reactions where useful.
- [ ] Community signals projected into the dashboard.
- [ ] Cross-reading of traffic, community, development context and curated events.

A stock change is not automatically a count of new events. For example, an open-issue delta can be affected by both issue creation and issue closure between snapshots. Community metrics remain repository-scoped unless an explicitly deduplicated semantic is introduced later.

The first retained community baseline is dated 2026-09-05. The scheduled run on the night of 2026-09-05 validated the M3b comparison pipeline but correctly remained a same-date replacement, so the first real cross-date stock delta is still pending.

Development activity context is explanatory evidence only. High first-party commit or workflow-run activity can make first-party/automation contamination more plausible, but does not prove that those activities caused GitHub traffic.

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
