# Development context review: 2026-09-02 to 2026-09-04

Status: initial M3c evidence review.

## Purpose

Review known high-clone days against retained first-party development and GitHub Actions activity.

This report provides context only. It does not attribute GitHub traffic to a specific workflow, developer action, bot, or external audience.

## 2026-09-02

Observed traffic highlights:

- Core: 910 clones, 230 repository-scoped unique cloners, 0 views.
- OpenOBSW / OpenSVF adapter: 142 clones, 2 repository-scoped unique cloners, 0 views.

Development context:

- Core: 5 commits, all classified first-party; 10 workflow runs, all successful.
- OpenOBSW / OpenSVF adapter: 1 first-party commit; 2 workflow runs.

Interpretation:

The day contains clear first-party development and automation context, while browsing evidence is absent. This makes first-party / CI contamination plausible, but the retained data does not identify the source of any individual clone.

## 2026-09-03

Observed traffic highlights:

- Core: 1,618 clones, 535 repository-scoped unique cloners, 0 views.
- F´ adapter: 137 clones, 1 repository-scoped unique cloner, 0 views.
- OpenC3 / COSMOS adapter: 142 clones, 12 repository-scoped unique cloners, 0 views.
- OpenOBSW / OpenSVF adapter: 437 clones, 43 repository-scoped unique cloners, 0 views.

Development context:

- Core: 0 commits, 0 workflow runs.
- F´ adapter: 72 first-party commits; 20 workflow runs.
- OpenC3 / COSMOS adapter: 7 first-party commits; 14 workflow runs.
- OpenOBSW / OpenSVF adapter: 46 first-party commits; 21 workflow runs.
- Across the three official adapters: 125 first-party commits and 55 workflow runs.

Interpretation:

This is the clearest example of why same-repository activity alone is insufficient context. Core had no direct default-branch commit or workflow-run activity, yet its clone count was very high while the adapter layer was under unusually intense first-party development and CI activity.

The retained evidence therefore supports an ecosystem-level contamination hypothesis more strongly than a simple same-repository explanation. It still does not prove that adapter workflows caused Core clones, because GitHub Traffic does not expose clone identity or source attribution.

The complete absence of views across these repositories also makes this day look more like technical access / automation-heavy activity than ordinary browsing-driven discovery, without proving that all traffic was first-party.

## 2026-09-04

Observed traffic highlights:

- Core: 1,305 clones, 456 repository-scoped unique cloners, 24 views / 2 repository-scoped unique viewers.
- F´ adapter: 242 clones, 18 repository-scoped unique cloners, 42 views / 2 repository-scoped unique viewers.
- OpenC3 / COSMOS adapter: 2 clones, 2 repository-scoped unique cloners, 9 views / 1 repository-scoped unique viewer.
- OpenOBSW / OpenSVF adapter: 18 clones, 10 repository-scoped unique cloners, 16 views / 3 repository-scoped unique viewers.

Development context:

- Core: 3 first-party commits; 6 successful workflow runs.
- F´ adapter: 21 first-party commits; 14 workflow runs.
- Other official adapters: no default-branch commits or workflow runs recorded that day.

Contextual events already retained for the day include F´ adapter releases and the upstream F´ discussion.

Interpretation:

September 4 is a mixed-evidence day. First-party development remains substantial, especially around the F´ adapter, but unlike September 2 and 3 there is also visible browsing activity and confirmed public ecosystem events.

That combination makes external attention plausible while keeping attribution unresolved. It should not be reduced either to "development traffic" or to "outreach impact".

## Initial conclusion

M3c materially improves interpretation of the clone spikes:

1. High clone activity can coincide with intense first-party development and CI activity.
2. Same-repository workflow counts are not sufficient to explain ecosystem traffic; cross-repository activity must remain part of the context.
3. A day with high clones and no views is qualitatively different from a day where browsing appears alongside public events.
4. None of these observations turns repository-scoped unique clone counts into external-user counts or establishes causal attribution.

The appropriate current interpretation remains contextual and confidence-aware rather than subtractive: retain the raw traffic, retain development context, and avoid inventing an "external clone" estimate.
