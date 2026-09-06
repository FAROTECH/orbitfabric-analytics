# Dashboard architecture

Status: accepted and operational.

## Decision

OrbitFabric Analytics uses a static, installable Progressive Web App for presentation.

The dashboard lives in the same `orbitfabric-analytics` repository under `dashboard/` and is deployed to Cloudflare Pages.

The current deployment policy is intentionally **public but unlisted**. Cloudflare Access is optional and can be introduced later if the dashboard starts containing information that should be treated as confidential.

## UI language

The dashboard is primarily for the maintainer and intentionally uses an Italian technical style with familiar English analytics/software terms.

Examples:

```text
Overview
Latest complete day
Coverage
Activity timeline
Event context
Ecosystem context
Repository comparison
Signal shape
```

Explanatory notes remain in Italian. No internationalization framework is introduced at this stage.

## Frontend stack

The implementation remains deliberately small:

```text
static HTML
CSS
vanilla JavaScript
Chart.js
PWA manifest
service worker
```

No React, Vue, Vite or application backend is required.

## Constraints

The dashboard architecture preserves these properties:

- no runtime backend;
- no GitHub token or repository credential in browser-side code;
- analytics semantics remain implemented before presentation;
- generated dashboard data is built by trusted automation;
- desktop and mobile PWA usage;
- portable static hosting;
- raw actor identity registries remain outside the public deployment artifact.

## Branch responsibilities

```text
main
    source code, configuration, documentation, dashboard source

github-repo-stats
    retained raw/history data and generated analytics datasets

dashboard-site
    deployable static dashboard snapshot, including dashboard_data.json
```

Generated dashboard data remains excluded from `main`. The daily workflow assembles dashboard source from `main` with the latest presentation payload from `github-repo-stats` and commits the deployable snapshot to `dashboard-site`.

Cloudflare Pages watches `dashboard-site` and serves the `dashboard/` directory.

## Data flow

```text
GitHub repositories
    -> traffic collection
    -> community stock collection
    -> lifecycle collection
    -> participation collection
    -> development activity collection

curated events
    -> normalized event context

all retained evidence
    -> analytics semantics
    -> official traffic rollups / comparison
    -> dashboard_data.json
    -> dashboard-site
    -> Cloudflare Pages
    -> browser / mobile PWA
```

The PWA consumes one generated presentation payload:

```text
analytics/dashboard_data.json
```

During deployment that file is exposed as:

```text
dashboard/data/dashboard_data.json
```

## Evidence families

The first operational dashboard presents six evidence families without collapsing their meanings:

```text
TRAFFIC
    clone / view activity

COMMUNITY STOCK
    stars / forks / open issues / open pull requests / contributor records

LIFECYCLE
    issue and pull-request lifecycle events

PARTICIPATION
    repository-scoped actor-bearing activity

DEVELOPMENT CONTEXT
    commits / workflow runs

CURATED CONTEXT
    releases / outreach / upstream discussions / community contributions
```

The browser does not infer causal relationships between these families.

## Time alignment

Traffic repository comparison uses a common recent window anchored to the latest complete ecosystem traffic day.

M3 lifecycle, participation and development context shown in the dashboard are aggregated over that same window:

```text
traffic comparison window
        =
lifecycle context window
        =
participation context window
        =
development context window
```

Community stock is different: it is a current repository-state snapshot and may legitimately be newer than the latest complete traffic day. The dashboard therefore exposes the stock snapshot date separately instead of silently forcing it onto the traffic timeline.

## Snapshot delta semantics

Traffic deltas are computed before the browser renders the dashboard.

For Overview:

```text
latest complete ecosystem day
vs
previous complete ecosystem day
```

For Repository Comparison:

```text
current rolling N-day snapshot
vs
previous complete rolling N-day snapshot
```

Community stock uses its own latest-vs-previous available snapshot contract and initially exposes absolute deltas only.

Repository-scoped unique traffic metrics remain repository-scoped. Their deltas must never be described as new people or ecosystem-wide unique users.

## Participation boundary

Participation data is repository-scoped.

`other` means an observed actor that is neither configured first-party nor automation. It does **not** automatically mean an external user or contributor.

Window totals such as participant presence are represented as sums of repository-day observations. They are not ecosystem-wide deduplicated people.

The cumulative actor registry used to preserve first-observed semantics remains on the private `github-repo-stats` branch and is not copied into `dashboard-site`.

## Presentation boundary

The frontend is responsible for:

- rendering overview metrics and deltas;
- rendering traffic charts;
- rendering curated event context;
- rendering community and engineering context already computed by analytics;
- rendering repository comparison tables;
- responsive desktop/mobile presentation.

It is not responsible for:

- classifying external users;
- removing bots or first-party traffic;
- computing adoption confidence;
- redefining coverage;
- deduplicating people across repositories;
- inventing causal attribution.

## Exposure and discoverability

The Cloudflare Pages production URL is technically public when Cloudflare Access is not enabled.

Current policy:

- do not link the dashboard from public OrbitFabric repositories, documentation or social profiles;
- publish only analytics information acceptable for public exposure;
- send `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet`;
- include an HTML robots directive;
- publish a `robots.txt` that disallows crawling.

These controls reduce discoverability but **are not authentication or confidentiality controls**.

If confidentiality becomes a requirement, Cloudflare Access can be enabled without changing the dashboard architecture.

## Security boundary

GitHub credentials remain inside GitHub Actions or another trusted build environment.

No secret required to read private GitHub data may be embedded in JavaScript, HTML, generated JSON or the PWA manifest.

The source repository remains private independently from the public visibility of the deployed Pages application.
