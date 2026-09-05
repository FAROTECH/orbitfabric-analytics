# Dashboard architecture

Status: accepted and implementation started in M1.

## Decision

OrbitFabric Analytics uses a static, installable Progressive Web App for presentation.

The dashboard lives in the same `orbitfabric-analytics` repository under `dashboard/` and will be deployed to Cloudflare Pages behind Cloudflare Access.

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

## Data flow

```text
GitHub repositories
    -> daily collection
    -> raw github-repo-stats data
    -> normalized analytics datasets
    -> official rollups
    -> repository comparison
    -> dashboard_data.json
    -> static PWA
    -> Cloudflare Pages
    -> Cloudflare Access
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

The generated JSON is not committed to `main`. It is persisted with the other generated datasets on the `github-repo-stats` branch and injected into the deployable site by trusted automation.

## Presentation boundary

The browser does not parse raw GHRS data and does not reproduce analytics logic.

The frontend is responsible for:

- rendering overview metrics;
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

## Security boundary

GitHub credentials remain inside GitHub Actions or another trusted build environment.

Cloudflare Access protects the deployed dashboard independently from the visibility of the source repository. The source repository remains private.

No secret required to read private GitHub data may be embedded in JavaScript, HTML, generated JSON or the PWA manifest.

## Deployment timing

Dashboard source and presentation-data generation are implemented before external deployment. Cloudflare Pages and Cloudflare Access configuration are performed as a separate validation step so that hosting credentials do not become a prerequisite for testing the analytics pipeline.
