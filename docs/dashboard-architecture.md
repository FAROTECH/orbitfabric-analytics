# Dashboard architecture

Status: accepted for M1 dashboard implementation.

## Decision

OrbitFabric Analytics will use a static, installable Progressive Web App for presentation.

The dashboard will live in the same `orbitfabric-analytics` repository under a future `dashboard/` directory and will be deployed to Cloudflare Pages behind Cloudflare Access.

## Constraints

The dashboard architecture must preserve these properties:

- no runtime application backend;
- no requirement to run a local process on a workstation;
- convenient browser access from desktop and mobile;
- installable PWA behavior on supported mobile devices;
- no GitHub API token or other repository credential in browser-side code;
- analytics semantics remain implemented in the analytics layer, not in the UI;
- generated dashboard data is built by trusted automation before deployment;
- hosting remains portable to another static provider if needed.

## Data flow

```text
GitHub repositories
    -> daily collection
    -> raw github-repo-stats data
    -> normalized analytics datasets
    -> derived comparison / interpretation datasets
    -> dashboard data build
    -> static PWA
    -> Cloudflare Pages
    -> Cloudflare Access
    -> browser / mobile PWA
```

The PWA will consume generated static data files, likely JSON prepared during the build. It will not query the private analytics repository directly at runtime.

## Security boundary

GitHub credentials remain inside GitHub Actions or another trusted build environment.

Cloudflare Access protects the deployed dashboard independently from the visibility of the source repository. The source repository remains private.

No secret required to read private GitHub data may be embedded in JavaScript, HTML, generated JSON or the PWA manifest.

## Deployment timing

The deployment mechanism is selected now, but the dashboard itself will be implemented only after M1 metric and comparison semantics are stable enough to define useful views.

This avoids designing charts first and inventing metric meaning inside the presentation layer.
