const orbitfabricEventGuidePlugin = {
  id: "orbitfabricEventGuide",
  afterDatasetsDraw(chart) {
    const index = chart.$orbitfabricEventIndex;
    if (!Number.isInteger(index)) {
      return;
    }
    if (!chart.canvas || !["clones-chart", "views-chart"].includes(chart.canvas.id)) {
      return;
    }

    const { ctx, chartArea, scales } = chart;
    if (!chartArea || !scales?.x) {
      return;
    }

    const x = scales.x.getPixelForValue(index);
    if (!Number.isFinite(x)) {
      return;
    }

    const accent = getComputedStyle(document.documentElement)
      .getPropertyValue("--accent")
      .trim() || "#68d5ff";

    ctx.save();
    ctx.strokeStyle = accent;
    ctx.fillStyle = accent;
    ctx.globalAlpha = 0.72;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(x, chartArea.top);
    ctx.lineTo(x, chartArea.bottom);
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.arc(x, chartArea.top + 5, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  },
};

if (typeof Chart !== "undefined") {
  Chart.register(orbitfabricEventGuidePlugin);
}

window.setOrbitfabricEventGuide = function setOrbitfabricEventGuide(index) {
  for (const chartId of ["clones-chart", "views-chart"]) {
    const chart = typeof Chart !== "undefined" ? Chart.getChart(chartId) : null;
    if (!chart) {
      continue;
    }
    chart.$orbitfabricEventIndex = Number.isInteger(index) ? index : null;
    chart.draw();
  }
};
