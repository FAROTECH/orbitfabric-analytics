# Dashboard architecture

Status: accepted and implementation started in M1.

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
Repository comparison
Activity timeline
Signal shape
Clone activity
View activity
```

Explanatory notes remain in Italian. No internationalization framework is introduced at this stage.

## Frontend stack

The first dashboard implementation is deliberately small:

```text
static HTML
CSS
vanilla JavaScript
Chart.js for charts
PWA manifest
service worker
```

No React, Vue, Vite or other frontend build framework is required for M1. The dashboard can be hosted by any static provider.

## Constraints

The dashboard architecture preserves these properties:

- no runtime application backend;
- no requirement to run a local process on a workstation for normal usage;
- convenient browser access from desktop and mobile;
- installable PWA behavior on supported devices;
- no GitHub API token or repository credential in browser-side code;
- analytics semantics remain implemented in the analytics layer, not in the UI;
- generated dashboard data is built by trusted automation before deployment;
- hosting remains portable to another static provider if needed.

## Branch responsibilities

```text
main
    source code, configuration, documentation, dashboard source

github-repo-stats
    retained raw/history data and generated analytics datasets

dashboard-site
    deployable static dashboard snapshot, including dashboard_data.json
```

Generated dashboard data remains excluded from `main`. The daily workflow assembles the dashboard source from `main` with the latest presentation payload from `github-repo-stats` and commits that deployable snapshot to `dashboard-site`.

Cloudflare Pages watches `dashboard-site` and serves the `dashboard/` directory.

## Data flow

```text
GitHub repositories
    -> daily collection
    -> raw github-repo-stats data
    -> normalized analytics datasets
    -> official rollups
    -> repository comparison
    -> snapshot deltas
    -> dashboard_data.json
    -> dashboard-site branch
    -> Cloudflare Pages
    -> browser / mobile PWA
```

The PWA consumes one generated presentation payload:

```text
analytics/dashboard_data.json
```

During deployment that file is exposed to the static application as:

```text
dashboard/data/dashboard_data.json
```

## Snapshot delta semantics

Snapshot deltas are computed before the browser renders the dashboard.

For the Overview cards:

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

The repository comparison windows therefore have the same length and are shifted by one complete ecosystem snapshot. This is a change-since-previous-snapshot signal, not a comparison against a disjoint historical period.

Each delta carries:

```text
current
previous
absolute
pct
state
```

`state` is one of `increase`, `decrease`, `unchanged` or `new`. If the previous value is zero and the current value is non-zero, percentage change is intentionally left undefined and the state is `new`.

Deltas are directional activity signals only. Higher is not automatically better and lower is not automatically worse.

Repository-scoped unique metrics remain repository-scoped. Their deltas must never be described as new people or ecosystem-wide unique users.

## Presentation boundary

The browser does not parse raw GHRS data and does not reproduce analytics logic.

The frontend is responsible for:

- rendering overview metrics;
- rendering snapshot deltas already computed by the analytics layer;
- rendering charts;
- rendering repository comparison tables;
- explaining already-defined metric semantics;
- responsive desktop/mobile presentation.

It is not responsible for:

- classifying external users;
- removing bots or first-party activity;
- computing adoption confidence;
- redefining coverage;
- inventing new metric semantics.

## Exposure and discoverability

The Cloudflare Pages production URL is technically public when Cloudflare Access is not enabled.

The current policy is therefore:

- do not link the dashboard from public OrbitFabric repositories, documentation or social profiles;
- publish only analytics information that is acceptable to expose publicly;
- send `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet` through the Pages `_headers` file;
- include an HTML `robots` meta directive;
- publish a `robots.txt` that disallows crawling.

These controls reduce discoverability but **are not authentication or confidentiality controls**. Anyone who knows or guesses the URL can access the deployed dashboard.

If confidentiality becomes a requirement, Cloudflare Access can be enabled without changing the dashboard architecture.

## Security boundary

GitHub credentials remain inside GitHub Actions or another trusted build environment.

No secret required to read private GitHub data may be embedded in JavaScript, HTML, generated JSON or the PWA manifest.

The source repository remains private independently from the public visibility of the deployed Pages application.

## Deployment

Cloudflare Pages is connected to the private GitHub repository. The production deployment uses the `dashboard-site` branch with `dashboard/` as the build output directory and no frontend build command.

This keeps Cloudflare credentials out of GitHub Actions: the workflow only updates a Git branch, while the existing Cloudflare Git integration handles deployment.
