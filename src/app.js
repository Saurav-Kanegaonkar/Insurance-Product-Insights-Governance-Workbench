const state = {
  payload: null,
  lineFilter: "All",
  selectedProductId: null,
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US");

const get = (id) => document.getElementById(id);

function pct(value) {
  return `${Number(value).toFixed(1)}%`;
}

function rowsForLine() {
  const rows = state.payload.priorityQueue;
  if (state.lineFilter === "All") {
    return rows;
  }
  return rows.filter((row) => row.line_of_business === state.lineFilter);
}

function renderKpis(rows) {
  const summary = state.payload.summary;
  const top = rows[0] || summary.top_priority;
  const premium = rows.reduce((sum, row) => sum + Number(row.earned_premium), 0);
  const avgPriority = rows.reduce((sum, row) => sum + Number(row.priority_score), 0) / rows.length;
  const highChecks = rows.reduce((sum, row) => sum + Number(row.open_high_quality_checks), 0);
  const items = [
    ["Segments in view", number.format(rows.length), `${number.format(summary.product_segments)} generated segments`],
    ["Premium in scope", money.format(premium), "Synthetic earned premium"],
    ["Avg priority score", Number(avgPriority).toFixed(1), "Higher means review sooner"],
    ["High DQ checks", number.format(highChecks), "May block decision confidence"],
    ["Top segment", `${top.product} ${top.state}`, top.channel],
  ];
  get("kpis").innerHTML = items
    .map(
      ([label, value, note]) => `
        <article class="kpi">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${note}</em>
        </article>
      `,
    )
    .join("");
}

function renderPriorityRows(rows) {
  get("priority-rows").innerHTML = rows
    .slice(0, 12)
    .map(
      (row) => `
        <tr>
          <td><button class="link-button" type="button" data-select="${row.product_id}">${row.product} <span>${row.state}, ${row.channel}</span></button></td>
          <td>${pct(row.combined_ratio)}</td>
          <td>${pct(row.kpi_quality_score)}</td>
          <td><b>${row.priority_score}</b></td>
          <td>${row.recommended_action}</td>
        </tr>
      `,
    )
    .join("");

  document.querySelectorAll("[data-select]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedProductId = button.dataset.select;
      activateView("diagnostic");
      renderSelectedSegment();
    });
  });
}

function renderSignalBars(rows) {
  const topRows = rows.slice(0, 6);
  get("signal-bars").innerHTML = topRows
    .map((row) => {
      const performance = Math.min(Number(row.combined_ratio), 130);
      const qualityRisk = 100 - Number(row.kpi_quality_score);
      const retentionRisk = 100 - Number(row.retention_rate);
      return `
        <div class="signal-row">
          <div>
            <b>${row.product}</b>
            <span>${row.state}, ${row.channel}</span>
          </div>
          <div class="bar-stack" aria-label="${row.product} signal mix">
            <span class="bar performance" style="width:${performance / 1.3}%"></span>
            <span class="bar quality" style="width:${qualityRisk}%"></span>
            <span class="bar retention" style="width:${retentionRisk}%"></span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderSegmentOptions() {
  get("segment-select").innerHTML = state.payload.priorityQueue
    .map(
      (row) => `
        <option value="${row.product_id}">${row.product} | ${row.state} | ${row.channel}</option>
      `,
    )
    .join("");
  if (!state.selectedProductId) {
    state.selectedProductId = state.payload.priorityQueue[0].product_id;
  }
  get("segment-select").value = state.selectedProductId;
}

function selectedRow() {
  return state.payload.priorityQueue.find((row) => row.product_id === state.selectedProductId) || state.payload.priorityQueue[0];
}

function renderSelectedSegment() {
  const row = selectedRow();
  state.selectedProductId = row.product_id;
  get("segment-select").value = row.product_id;
  get("selected-name").textContent = `${row.product} in ${row.state} through ${row.channel}`;
  get("selected-action").textContent = row.recommended_action;
  get("selected-metrics").innerHTML = [
    ["Combined ratio", pct(row.combined_ratio)],
    ["Retention", pct(row.retention_rate)],
    ["New business growth", pct(row.new_business_growth)],
    ["Claims satisfaction", pct(row.claims_satisfaction)],
    ["KPI quality", pct(row.kpi_quality_score)],
    ["Open high checks", row.open_high_quality_checks],
  ]
    .map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`)
    .join("");

  const metrics = [
    ["Combined ratio", row.combined_ratio, 125, "performance"],
    ["Retention risk", 100 - Number(row.retention_rate), 35, "retention"],
    ["Growth signal", row.new_business_growth, 20, "growth"],
    ["KPI quality risk", 100 - Number(row.kpi_quality_score), 40, "quality"],
    ["Priority score", row.priority_score, 155, "priority"],
  ];
  get("driver-profile").innerHTML = metrics
    .map(
      ([label, value, max, kind]) => `
        <div class="driver-row">
          <div><b>${label}</b><span>${Number(value).toFixed(1)}</span></div>
          <meter class="${kind}" min="0" max="${max}" value="${value}"></meter>
        </div>
      `,
    )
    .join("");
}

function renderMarketTrends() {
  get("market-trends").innerHTML = state.payload.marketTrends
    .map(
      (trend) => `
        <article class="trend">
          <b>${trend.trend}</b>
          <p>${trend.modeled_assumption}</p>
          <span>${trend.analyst_response}</span>
        </article>
      `,
    )
    .join("");
}

function renderGovernance() {
  get("quality-rows").innerHTML = state.payload.qualityQueue
    .slice(0, 16)
    .map(
      (row) => `
        <tr>
          <td>${row.check_name}<span>${row.severity}, ${row.status}</span></td>
          <td>${row.impacted_metric}</td>
          <td>${row.source_system}</td>
          <td><b>${pct(row.failed_row_rate)}</b></td>
          <td>${row.owner}</td>
        </tr>
      `,
    )
    .join("");
}

function renderBrief() {
  get("stakeholder-requests").innerHTML = state.payload.stakeholderRequests
    .map(
      (request) => `
        <article class="request">
          <span>${request.request_type}</span>
          <b>${request.business_question}</b>
          <em>${request.decision_owner}, ${request.status}</em>
        </article>
      `,
    )
    .join("");

  get("action-rows").innerHTML = state.payload.actionPlan
    .slice(0, 12)
    .map(
      (row) => `
        <tr>
          <td>${row.rank}</td>
          <td>${row.management_question}</td>
          <td>${row.owner}</td>
          <td>${row.next_artifact}</td>
        </tr>
      `,
    )
    .join("");
}

function renderHero() {
  const top = state.payload.summary.top_priority;
  get("top-product").textContent = `${top.product} ${top.state}, ${top.channel}`;
  get("top-action").textContent = top.recommended_action;
}

function renderCockpit() {
  const rows = rowsForLine();
  renderKpis(rows);
  renderPriorityRows(rows);
  renderSignalBars(rows);
}

function activateView(viewId) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.view === viewId);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("is-active", view.id === viewId);
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  renderHero();
  renderSegmentOptions();
  renderCockpit();
  renderSelectedSegment();
  renderMarketTrends();
  renderGovernance();
  renderBrief();

  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => activateView(button.dataset.view));
  });

  get("line-filter").addEventListener("change", (event) => {
    state.lineFilter = event.target.value;
    renderCockpit();
  });

  get("segment-select").addEventListener("change", (event) => {
    state.selectedProductId = event.target.value;
    renderSelectedSegment();
  });
}

init().catch((error) => {
  document.body.innerHTML = `<main class="shell"><section class="panel"><h1>Unable to load workbench data</h1><p>${error.message}</p></section></main>`;
});
