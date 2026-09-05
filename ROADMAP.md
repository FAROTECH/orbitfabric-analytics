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

**Status: in progress**

Goal: compare traffic changes with relevant project events without turning temporal proximity into causal claims.

Current baseline:

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
- [ ] First automated interactive traffic/event overlay deployment validated end to end.
- [x] Initial set of confirmed public OrbitFabric events curated.
- [ ] First traffic/event correlation review completed.

Planned event classes include releases, outreach, upstream discussions, documentation launches, internal milestones and major ecosystem milestones. Channels are policy-driven and currently include GitHub, LinkedIn, Reddit, Hackaday, Libre Space, website and internal analytics context.

Historical events are not invented merely to populate the dashboard. When a date is uncertain but still useful, it is explicitly marked `approximate`; confirmed day-level correlation uses `confirmed` events.

The event context distinguishes events already inside the retained traffic window from events awaiting a future complete traffic day and events older than the retained timeline. This keeps the dashboard explicit about whether correlation can actually be inspected yet.

The traffic/event overlay is intentionally interaction-driven: the rail is always visible, while a thin guide is drawn across both traffic charts only when an in-window event day is selected. This avoids permanently cluttering the charts and keeps the interaction usable on small screens.

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
