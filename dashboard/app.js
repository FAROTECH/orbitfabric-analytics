const DATA_URL = "./data/dashboard_data.json";

const repositoryLabels = {
  core: "Core",
  studio: "Studio",
  "reference-mission": "Reference Mission",
  "openobsw-opensvf-adapter": "OpenOBSW / OpenSVF",
  "openc3-cosmos-adapter": "OpenC3 / COSMOS",
  "fprime-adapter": "F´ Adapter",
};

const scopeLabels = {
  core: "Core",
  product: "Product",
  adapter: "Adapters",
};

const css = getComputedStyle(document.documentElement);
const palette = {
  core: css.getPropertyValue("--core").trim(),
  product: css.getPropertyValue("--product").trim(),
  adapter: css.getPropertyValue("--adapter").trim(),
  cloneOnly: css.getPropertyValue("--clone-only").trim(),
  mixed: css.getPropertyValue("--mixed").trim(),
  viewOnly: css.getPropertyValue("--view-only").trim(),
  inactive: css.getPropertyValue("--inactive").trim(),
  text: css.getPropertyValue("--text").trim(),
  muted: css.getPropertyValue("--muted").trim(),
  line: css.getPropertyValue("--line").trim(),
};

const numberFormat = new Intl.NumberFormat("it-IT");
const fullDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});
const shortDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
});

function asDate(value) {
  return new Date(`${value}T12:00:00Z`);
}

function formatNumber(value) {
  return numberFormat.format(value ?? 0);
}

function formatFullDate(value) {
  return fullDateFormat.format(asDate(value));
}

function formatShortDate(value) {
  return shortDateFormat.format(asDate(value));
}

function repositoryLabel(repository) {
  return repositoryLabels[repository.repository_id] ?? repository.repository_id;
}

function renderOverview(data) {
  const overview = data.overview;
  document.querySelector("#latest-day").textContent = formatFullDate(
    data.latest_complete_day,
  );
  document.querySelector("#coverage").textContent = `${overview.coverage_pct}%`;
  document.querySelector("#coverage-detail").textContent =
    `${overview.repositories_available}/${overview.repositories_expected} repository disponibili`;
  document.querySelector("#clones-total").textContent = formatNumber(
    overview.clones_total,
  );
  document.querySelector("#views-total").textContent = formatNumber(
    overview.views_total,
  );
  document.querySelector("#data-status").textContent =
    `Data complete fino al ${formatFullDate(data.latest_complete_day)}`;
}

function baseChartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: palette.muted,
          boxWidth: 10,
          boxHeight: 10,
          padding: 18,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: "rgba(8, 17, 31, 0.96)",
        borderColor: palette.line,
        borderWidth: 1,
        titleColor: palette.text,
        bodyColor: palette.text,
        padding: 12,
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: { display: false },
        ticks: {
          color: palette.muted,
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 7,
        },
        border: { color: palette.line },
      },
      y: {
        stacked: true,
        beginAtZero: true,
        grid: { color: palette.line },
        ticks: {
          color: palette.muted,
          precision: 0,
        },
        border: { display: false },
      },
    },
  };
}

function timelineDataset(data, scopeId, metric) {
  return data.timeline.map((point) => point.categories?.[scopeId]?.[metric] ?? 0);
}

function renderTimelineCharts(data) {
  const labels = data.timeline.map((point) => formatShortDate(point.date));
  const scopes = ["core", "product", "adapter"];

  const makeDatasets = (metric) =>
    scopes.map((scopeId) => ({
      label: scopeLabels[scopeId],
      data: timelineDataset(data, scopeId, metric),
      backgroundColor: palette[scopeId],
      borderColor: palette[scopeId],
      borderWidth: 0,
      borderRadius: 3,
      maxBarThickness: 30,
    }));

  new Chart(document.querySelector("#clones-chart"), {
    type: "bar",
    data: {
      labels,
      datasets: makeDatasets("clones_total"),
    },
    options: baseChartOptions(),
  });

  new Chart(document.querySelector("#views-chart"), {
    type: "bar",
    data: {
      labels,
      datasets: makeDatasets("views_total"),
    },
    options: baseChartOptions(),
  });
}

function renderComparison(data) {
  const comparison = data.comparison;
  document.querySelector("#comparison-window").textContent =
    `${formatFullDate(comparison.window_start)} → ${formatFullDate(comparison.window_end)} · ${comparison.window_days} giorni`;

  const body = document.querySelector("#comparison-body");
  body.replaceChildren();

  for (const repository of comparison.repositories) {
    const row = document.createElement("tr");
    const ratio = repository.clone_to_view_ratio;
    const coverageClass = repository.coverage_complete ? "complete" : "partial";
    const fullName = repository.repository;

    row.innerHTML = `
      <td>
        <div class="repo-name">
          <strong>${repositoryLabel(repository)}</strong>
          <span>${fullName}</span>
        </div>
      </td>
      <td><span class="category-pill" data-category="${repository.category}">${repository.category}</span></td>
      <td>${formatNumber(repository.clones_total)}</td>
      <td>${formatNumber(repository.views_total)}</td>
      <td>${formatNumber(repository.clone_only_days)}</td>
      <td>${formatNumber(repository.mixed_days)}</td>
      <td>${formatNumber(repository.view_only_days)}</td>
      <td>${ratio === null ? "—" : ratio.toLocaleString("it-IT")}</td>
      <td><span class="coverage-pill ${coverageClass}">${repository.coverage_pct}%</span></td>
    `;
    body.appendChild(row);
  }
}

function renderSignalShape(data) {
  const repositories = data.comparison.repositories;
  const labels = repositories.map(repositoryLabel);

  const options = baseChartOptions();
  options.indexAxis = "y";
  options.interaction = { intersect: false, mode: "index" };
  options.scales.x.max = data.comparison.window_days;
  options.scales.x.ticks.stepSize = 1;
  options.scales.y.ticks.autoSkip = false;
  options.scales.y.ticks.color = palette.text;

  new Chart(document.querySelector("#signal-shape-chart"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Clone-only",
          data: repositories.map((row) => row.clone_only_days),
          backgroundColor: palette.cloneOnly,
          borderWidth: 0,
        },
        {
          label: "Mixed",
          data: repositories.map((row) => row.mixed_days),
          backgroundColor: palette.mixed,
          borderWidth: 0,
        },
        {
          label: "View-only",
          data: repositories.map((row) => row.view_only_days),
          backgroundColor: palette.viewOnly,
          borderWidth: 0,
        },
        {
          label: "Inactive",
          data: repositories.map((row) => row.inactive_days),
          backgroundColor: palette.inactive,
          borderWidth: 0,
        },
      ],
    },
    options,
  });
}

function showFatalError(error) {
  console.error(error);
  const panel = document.querySelector("#fatal-error");
  const detail = document.querySelector("#fatal-error-detail");
  detail.textContent = error instanceof Error ? error.message : String(error);
  panel.hidden = false;
  document.querySelector("#data-status").textContent = "Data unavailable";
}

async function loadDashboard() {
  const response = await fetch(DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`dashboard_data.json: HTTP ${response.status}`);
  }

  const data = await response.json();
  if (data.schema_version !== 1) {
    throw new Error(`Unsupported dashboard schema: ${data.schema_version}`);
  }
  if (typeof Chart === "undefined") {
    throw new Error("Chart library unavailable");
  }

  renderOverview(data);
  renderTimelineCharts(data);
  renderComparison(data);
  renderSignalShape(data);
}

loadDashboard().catch(showFatalError);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch((error) => {
      console.warn("Service worker registration failed", error);
    });
  });
}
