const CONTEXT_DATA_URL = "./data/dashboard_data.json";

const contextNumberFormat = new Intl.NumberFormat("it-IT");
const contextDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

function contextAsDate(value) {
  return new Date(`${value}T12:00:00Z`);
}

function contextNumber(value) {
  return contextNumberFormat.format(value ?? 0);
}

function contextDate(value) {
  return contextDateFormat.format(contextAsDate(value));
}

function contextSigned(value) {
  if (value === null || value === undefined) {
    return "—";
  }
  if (value === 0) {
    return "0";
  }
  return `${value > 0 ? "+" : "-"}${contextNumber(Math.abs(value))}`;
}

function setContextText(selector, value) {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = value;
  }
}

function contextCell(value, delta = null) {
  const deltaMarkup = delta === null || delta === undefined
    ? ""
    : `<span class="context-table-delta">${contextSigned(delta)}</span>`;
  return `<div class="context-table-value"><span>${contextNumber(value)}</span>${deltaMarkup}</div>`;
}

function repositoryContextLabel(repositoryId) {
  const labels = {
    core: "Core",
    studio: "Studio",
    "reference-mission": "Reference Mission",
    "openobsw-opensvf-adapter": "OpenOBSW / OpenSVF",
    "openc3-cosmos-adapter": "OpenC3 / COSMOS",
    "fprime-adapter": "F´ Adapter",
  };
  return labels[repositoryId] ?? repositoryId;
}

function renderContextSummary(context) {
  const stock = context.stock;
  const aligned = context.aligned_window;
  const stockTotals = stock.totals;
  const lifecycle = aligned.lifecycle;
  const participation = aligned.participation;
  const development = aligned.development;

  setContextText("#context-stock-value", contextNumber(stockTotals.stars_total));
  setContextText(
    "#context-stock-detail",
    `${contextNumber(stockTotals.forks_total)} forks · ${contextNumber(stockTotals.open_issues_total)} open issues · ${contextNumber(stockTotals.open_pull_requests_total)} open PRs`,
  );
  setContextText(
    "#context-stock-delta",
    stock.comparable
      ? `Δ stars ${contextSigned(stockTotals.stars_total_delta)} · forks ${contextSigned(stockTotals.forks_total_delta)}`
      : "no comparable stock snapshot",
  );

  setContextText("#context-lifecycle-value", `${contextNumber(lifecycle.prs_merged)} merged`);
  setContextText(
    "#context-lifecycle-detail",
    `${contextNumber(lifecycle.prs_opened)} PR opened · ${contextNumber(lifecycle.prs_closed_unmerged)} closed unmerged · ${contextNumber(lifecycle.issues_opened)}/${contextNumber(lifecycle.issues_closed)} issues opened/closed`,
  );

  setContextText(
    "#context-participation-value",
    `${contextNumber(participation.other_participants_repo_count)} other`,
  );
  setContextText(
    "#context-participation-detail",
    `${contextNumber(participation.participants_repo_count)} participant repo-days · ${contextNumber(participation.other_participants_first_seen_repo_count)} other first-observed repo records`,
  );

  setContextText(
    "#context-development-value",
    contextNumber(development.first_party_commits),
  );
  setContextText(
    "#context-development-detail",
    `first-party commits · ${contextNumber(development.workflow_runs_total)} workflow runs · ${contextNumber(development.automation_commits)} automation commits`,
  );

  setContextText(
    "#context-window-note",
    `Community stock: ${contextDate(stock.current_date)}${stock.previous_date ? ` · Δ vs ${contextDate(stock.previous_date)}` : ""}. Activity context aligned to traffic: ${contextDate(aligned.window_start)} → ${contextDate(aligned.window_end)} (${aligned.window_days} days).`,
  );
}

function renderContextTable(context) {
  const body = document.querySelector("#context-repository-body");
  if (!body) {
    return;
  }
  body.replaceChildren();

  for (const repository of context.aligned_window.repositories) {
    const row = document.createElement("tr");
    const stock = repository.stock;
    const lifecycle = repository.lifecycle;
    const participation = repository.participation;
    const development = repository.development;

    row.innerHTML = `
      <td>
        <div class="repo-name">
          <strong>${repositoryContextLabel(repository.repository_id)}</strong>
          <span>${repository.repository}</span>
        </div>
      </td>
      <td>${contextCell(stock.stars_total, stock.stars_total_delta)}</td>
      <td>${contextCell(stock.forks_total, stock.forks_total_delta)}</td>
      <td>${contextCell(stock.open_issues_total, stock.open_issues_total_delta)}</td>
      <td>${contextCell(stock.open_pull_requests_total, stock.open_pull_requests_total_delta)}</td>
      <td>${contextNumber(lifecycle.prs_merged)}</td>
      <td>${contextNumber(participation.other_participants_repo_count)}</td>
      <td>${contextNumber(development.first_party_commits)}</td>
      <td>${contextNumber(development.workflow_runs_total)}</td>
    `;
    body.appendChild(row);
  }
}

async function loadEcosystemContext() {
  const response = await fetch(CONTEXT_DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`dashboard_data.json: HTTP ${response.status}`);
  }
  const data = await response.json();
  if (!data.ecosystem_context) {
    return;
  }

  renderContextSummary(data.ecosystem_context);
  renderContextTable(data.ecosystem_context);
}

loadEcosystemContext().catch((error) => {
  console.warn("Ecosystem context unavailable", error);
  setContextText("#context-window-note", "Community & engineering context unavailable.");
});
