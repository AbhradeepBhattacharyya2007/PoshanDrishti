let appState = {
  children: [],
  recipes: [],
  stateStaples: {},
  stats: null
};

let selectedRegionState = "Karnataka";
let charts = {};

// Load initial multi-state records & statistics from Python Flask backend
async function loadBackendBootstrap() {
  const res = await fetch("/api/bootstrap");
  const data = await res.json();
  appState = data;

  // Update Home KPIs
  document.getElementById("kpi-total-kids").innerText = `${data.stats.total} Children`;
  document.getElementById("kpi-states-sub").innerText = `Across ${data.stats.statesCovered} Indian States & UTs`;
  document.getElementById("kpi-normal-kids").innerText = `${data.stats.normal} Kids`;
  document.getElementById("kpi-mam-kids").innerText = `${data.stats.mam} Kids`;
  document.getElementById("kpi-sam-kids").innerText = `${data.stats.sam} Kids`;

  populateStateDropdown();
  populatePDFChildDropdown();
  renderAnalyticsCharts();
  renderRegistryTable();
  renderIndiaMap();
  renderRecipeBank();
}

function switchView(targetId) {
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.target === targetId);
  });
  document.getElementById(`view-${targetId}`).classList.add("active");

  if (targetId === "analytics") renderAnalyticsCharts();
  if (targetId === "india-map") renderIndiaMap();
  if (targetId === "ai-lab") updateBudgetSimulator();
  if (targetId === "recipes") renderRecipeBank();
  if (targetId === "health-card") renderHealthCardPreview();
}

document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => switchView(btn.dataset.target));
});

// =========================================================
// ANALYTICS CHARTS & REGISTRY TABLE
// =========================================================
function destroyChart(key) {
  if (charts[key]) charts[key].destroy();
}

function renderAnalyticsCharts() {
  if (!appState.stats) return;
  const s = appState.stats;

  // 1. Doughnut Chart: Triage Distribution
  destroyChart("doughnut");
  charts.doughnut = new Chart(document.getElementById("triageDoughnutChart"), {
    type: "doughnut",
    data: {
      labels: ["Normal Growth (Green)", "MAM Watchlist (Yellow)", "SAM Critical (Red)"],
      datasets: [{
        data: [s.normal, s.mam, s.sam],
        backgroundColor: ["#15803d", "#eab308", "#dc2626"],
        borderWidth: 2
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 2. Grouped Bar Chart: Age Cohorts
  destroyChart("cohort");
  const cohortLabels = Object.keys(s.cohorts);
  charts.cohort = new Chart(document.getElementById("cohortBarChart"), {
    type: "bar",
    data: {
      labels: cohortLabels,
      datasets: [
        { label: "Normal", data: cohortLabels.map(k => s.cohorts[k][0]), backgroundColor: "#15803d" },
        { label: "MAM", data: cohortLabels.map(k => s.cohorts[k][1]), backgroundColor: "#eab308" },
        { label: "SAM", data: cohortLabels.map(k => s.cohorts[k][2]), backgroundColor: "#dc2626" }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 3. Multi-Line Trend Chart: 6-Month Trajectory
  destroyChart("trend");
  charts.trend = new Chart(document.getElementById("trendLineChart"), {
    type: "line",
    data: {
      labels: ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
      datasets: [
        { label: "Healthy Growth (%)", data: [76.2, 78.0, 79.8, 81.5, 83.4, 85.1], borderColor: "#15803d", backgroundColor: "rgba(21,128,61,0.1)", fill: true, tension: 0.35 },
        { label: "THR Delivery (%)", data: [85.0, 87.5, 89.2, 91.4, 93.0, 94.8], borderColor: "#ea580c", tension: 0.35 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 70, max: 100 } } }
  });

  // 4. Radar Chart: Micronutrient Adequacy
  destroyChart("radar");
  charts.radar = new Chart(document.getElementById("nutrientRadarChart"), {
    type: "radar",
    data: {
      labels: ["Energy (kcal)", "Protein (g)", "Iron (mg)", "Vitamin A", "Calcium", "Zinc"],
      datasets: [
        { label: "Standard ICDS Meal (%)", data: [78, 74, 62, 70, 72, 65], borderColor: "#94a3b8", backgroundColor: "rgba(148,163,184,0.15)" },
        { label: "PoshanDrishti Millet-Fortified (%)", data: [96, 94, 91, 89, 95, 88], borderColor: "#1e3a8a", backgroundColor: "rgba(30,58,138,0.18)" }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 100 } } }
  });
}

function populateStateDropdown() {
  const sel = document.getElementById("registry-state-filter");
  const states = [...new Set(appState.children.map(c => c.state))].sort();
  sel.innerHTML = `<option value="All">All States & UTs (${states.length})</option>` +
    states.map(st => `<option value="${st}">${st}</option>`).join("");
}

function renderRegistryTable() {
  const stFilter = document.getElementById("registry-state-filter").value;
  const statusFilter = document.getElementById("registry-status-filter").value;
  const tbody = document.getElementById("registry-table-body");

  const filtered = appState.children.filter(c =>
    (stFilter === "All" || c.state === stFilter) &&
    (statusFilter === "All" || c.status === statusFilter)
  );

  tbody.innerHTML = filtered.map(c => `
    <tr>
      <td><b>${c.name}</b></td>
      <td>${c.age} mos (${c.gender[0]})</td>
      <td>${c.city}, <b>${c.state}</b></td>
      <td>${c.weight} kg / ${c.height} cm</td>
      <td><span class="status-badge status-${c.status}">${c.status} (${c.zScore})</span></td>
      <td>${c.condition || "Routine Check"}</td>
      <td style="white-space:nowrap;">
        <button class="btn-tiny" onclick="openChildPDF(${c.id})">🪪 PDF</button>
        <button class="btn-tiny" onclick="deleteChildRecord(${c.id})" title="Remove">🗑️</button>
      </td>
    </tr>
  `).join("");
}

function openChildPDF(childId) {
  const idx = appState.children.findIndex(c => c.id === childId);
  if (idx >= 0) {
    document.getElementById("pdf-child-select").value = idx;
    switchView("health-card");
  }
}

async function deleteChildRecord(childId) {
  await fetch(`/api/children/${childId}`, { method: "DELETE" });
  await loadBackendBootstrap();
}

// =========================================================
// INTERACTIVE INDIA REGIONAL MAP
// =========================================================
function renderIndiaMap() {
  const zone = document.getElementById("zone-filter").value;
  const metric = document.getElementById("map-metric-select").value;
  const layer = document.getElementById("map-nodes-layer");
  layer.innerHTML = "";

  const filtered = zone === "All" ? INDIA_REGIONS : INDIA_REGIONS.filter(r => r.zone === zone);

  filtered.forEach(reg => {
    let color = "#15803d";
    if (metric === "normal") color = reg.normal >= 84 ? "#15803d" : reg.normal >= 80 ? "#ea580c" : "#dc2626";
    else if (metric === "sam") color = reg.sam <= 2.8 ? "#15803d" : reg.sam <= 4.2 ? "#ea580c" : "#dc2626";
    else color = reg.thr >= 94 ? "#15803d" : reg.thr >= 90 ? "#ea580c" : "#dc2626";

    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", "state-node");
    g.onclick = () => selectRegionDetails(reg.state);

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", reg.x);
    circle.setAttribute("cy", reg.y);
    circle.setAttribute("r", reg.state === selectedRegionState ? 15 : 11);
    circle.setAttribute("fill", color);
    circle.setAttribute("stroke", reg.state === selectedRegionState ? "#facc15" : "#ffffff");
    circle.setAttribute("stroke-width", reg.state === selectedRegionState ? "3.5" : "2");

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", reg.x + 13);
    label.setAttribute("y", reg.y + 4);
    label.setAttribute("class", "state-label");
    label.textContent = reg.state;

    g.appendChild(circle);
    g.appendChild(label);
    layer.appendChild(g);
  });

  if (!filtered.some(r => r.state === selectedRegionState) && filtered.length) {
    selectedRegionState = filtered[0].state;
  }
  selectRegionDetails(selectedRegionState);

  destroyChart("regionalBar");
  charts.regionalBar = new Chart(document.getElementById("regionalBarChart"), {
    type: "bar",
    data: {
      labels: filtered.map(r => r.state),
      datasets: [
        { label: "Normal (%)", data: filtered.map(r => r.normal), backgroundColor: "#15803d" },
        { label: "MAM (%)", data: filtered.map(r => r.mam), backgroundColor: "#eab308" },
        { label: "SAM (%)", data: filtered.map(r => r.sam), backgroundColor: "#dc2626" }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, max: 100 } } }
  });
}

function selectRegionDetails(stateName) {
  selectedRegionState = stateName;
  const reg = INDIA_REGIONS.find(r => r.state === stateName) || INDIA_REGIONS[0];
  const staples = appState.stateStaples[stateName] || "Rice, Wheat & Pulses";
  const regKids = appState.children.filter(c => c.state === stateName);

  document.getElementById("region-detail-box").innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="color:#1e3a8a; font-size:1.35rem;">🇮🇳 ${reg.state}</h3>
      <span class="badge-jan">${reg.zone} Zone</span>
    </div>
    <p style="font-size:0.86rem; color:#475569; margin:6px 0 12px;">
      Anganwadi Centers: <b>${reg.awcs.toLocaleString()}</b> • Registry Cases: <b>${regKids.length} Children</b>
    </p>
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; padding:10px 12px; border-radius:10px; font-size:0.88rem;">
      <div>🌾 <b>Local Staples:</b> ${staples}</div>
      <div style="margin-top:4px;">🏛️ <b>State Child Scheme:</b> ${reg.scheme}</div>
    </div>
    <div class="stat-trio">
      <div class="stat-box green"><strong>${reg.normal}%</strong><br><small>NORMAL</small></div>
      <div class="stat-box yellow"><strong>${reg.mam}%</strong><br><small>MAM</small></div>
      <div class="stat-box red"><strong>${reg.sam}%</strong><br><small>SAM</small></div>
    </div>
    <p style="font-size:0.86rem; font-weight:700; color:#1e3a8a;">
      📦 Take-Home Ration (THR) Coverage: ${reg.thr}%
    </p>
  `;
}

// =========================================================
// CHILD GROWTH ASSESSOR (CALLS PYTHON FLASK /api/assess)
// =========================================================
async function handleChildAssessment(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById("child-name").value,
    age: document.getElementById("child-age").value,
    gender: document.getElementById("child-gender").value,
    height: document.getElementById("child-height").value,
    weight: document.getElementById("child-weight").value,
    city: document.getElementById("child-city").value,
    condition: document.getElementById("child-condition").value
  };

  const resDiv = document.getElementById("assessor-results");
  resDiv.style.display = "block";
  resDiv.innerHTML = `<div class="glass-card">⏳ Python backend is fetching live Open-Meteo weather & calculating WHO Z-scores...</div>`;

  const res = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await res.json();

  if (!res.ok) {
    resDiv.innerHTML = `<div class="glass-card">❌ ${data.error}</div>`;
    return;
  }

  // Refresh global registry & charts
  await loadBackendBootstrap();

  const { record, weather, triage, plan } = data;
  const labels = ["Option 1: Hot Cooked Meal", "Option 2: Take-Home Ration (THR)", "Option 3: Climate Hydration / Thermal Feed"];
  const mealCards = plan.meals.map((m, idx) => `
    <div class="recipe-card">
      <span class="badge-jan">${labels[idx]}</span>
      <h4 style="margin-top:8px; color:#1e3a8a;">${m.name}</h4>
      <div class="recipe-meta">
        <span class="tag">💰 ₹${m.cost.toFixed(2)}</span>
        <span class="tag">🔥 ${m.kcal} kcal</span>
        <span class="tag">💪 ${m.protein}g Protein</span>
      </div>
      <details class="recipe-drawer">
        <summary>📖 View Recipe & Ingredients</summary>
        <ul>${m.ingredients.map(i => `<li><b>${i.qty} ${i.unit}</b> ${i.item}</li>`).join("")}</ul>
        <ol>${m.steps.map(s => `<li>${s}</li>`).join("")}</ol>
      </details>
    </div>
  `).join("");

  resDiv.innerHTML = `
    <div class="glass-card top-navy">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
          <h3>✅ Saved & Assessed: ${record.name} (${record.age}m, ${record.gender})</h3>
          <p style="font-size:0.9rem; color:#475569;">
            📍 <b>${weather.city}, ${weather.state}</b> (${weather.lat}°N, ${weather.lon}°E) • Live Temp: <b>${weather.temp}°C</b> (${weather.climateLabel})
          </p>
        </div>
        <span class="status-badge status-${triage.status}">WHO Status: ${triage.status} (Z-Score: ${triage.zScore})</span>
      </div>
      <div style="background:#fff7ed; border-left:4px solid #ea580c; padding:10px 14px; border-radius:8px; margin:1rem 0; font-size:0.9rem;">
        🌾 <b>Regional Agricultural Staples (${weather.state}):</b> ${weather.staples}<br>
        🩺 <b>Clinical Protocol:</b> ${plan.boosterNote}
      </div>
      <div class="three-col-grid">${mealCards}</div>
    </div>
  `;
}

// =========================================================
// AI INNOVATION LAB (RADAR & BUDGET SIMULATOR)
// =========================================================
async function runClimateRadar() {
  const outBox = document.getElementById("radar-output");
  outBox.style.display = "block";
  outBox.innerHTML = "⏳ Running Python climate-malnutrition model...";

  const res = await fetch("/api/radar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      city: document.getElementById("radar-city").value,
      samRate: document.getElementById("radar-sam").value,
      water: document.getElementById("radar-water").value
    })
  });
  const data = await res.json();
  if (!res.ok) {
    outBox.innerHTML = `❌ ${data.error}`;
    return;
  }

  outBox.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
      <strong>14-Day Vulnerability Index: ${data.riskScore} / 100</strong>
      <span class="status-badge status-${data.badge}">${data.level}</span>
    </div>
    <p style="font-size:0.88rem; margin-bottom:6px;">
      📍 <b>${data.weather.city}, ${data.weather.state}</b> • Live Temp: <b>${data.weather.temp}°C</b> (${data.weather.climateLabel})<br>
      🌾 <b>Indigenous Shield Crops:</b> ${data.weather.staples}
    </p>
    <p style="font-size:0.88rem; color:#1e3a8a; font-weight:700;">${data.directive}</p>
  `;
}

function updateBudgetSimulator() {
  const baseBudget = parseFloat(document.getElementById("sim-budget").value);
  document.getElementById("sim-budget-val").innerText = `₹${baseBudget.toFixed(2)}`;
  const addEgg = document.getElementById("sim-egg").checked;
  const addMillet = document.getElementById("sim-millet").checked;

  const totalCost = baseBudget + (addEgg ? 2.5 : 0) + (addMillet ? 1.5 : 0);
  const protein = (baseBudget * 1.45 + (addEgg ? 6.5 : 0) + (addMillet ? 4.8 : 0)).toFixed(1);
  const kcal = Math.round(baseBudget * 42 + (addEgg ? 85 : 0) + (addMillet ? 110 : 0));
  const recoveryWeeks = Math.max(4, (18 - protein * 0.32 - kcal * 0.008).toFixed(1));

  document.getElementById("sim-metrics-grid").innerHTML = `
    <div class="sim-pill"><small>Effective Cost / Day</small><strong>₹${totalCost.toFixed(2)}</strong></div>
    <div class="sim-pill"><small>Daily Protein</small><strong>${protein} g</strong></div>
    <div class="sim-pill"><small>Daily Energy</small><strong>${kcal} kcal</strong></div>
    <div class="sim-pill"><small>Est. SAM Recovery</small><strong>${recoveryWeeks} Weeks</strong></div>
  `;

  const weeks = Array.from({ length: 13 }, (_, i) => `Wk ${i}`);
  const staticZ = weeks.map((_, w) => Number((-3.2 + w * 0.09).toFixed(2)));
  const gainRate = Math.min(0.28, protein / 110);
  const optZ = weeks.map((_, w) => Number(Math.min(0.2, -3.2 + w * gainRate).toFixed(2)));

  destroyChart("recovery");
  charts.recovery = new Chart(document.getElementById("recoveryCurveChart"), {
    type: "line",
    data: {
      labels: weeks,
      datasets: [
        { label: "Standard Static Meal", data: staticZ, borderColor: "#94a3b8", tension: 0.3 },
        { label: "PoshanDrishti Optimized", data: optZ, borderColor: "#15803d", backgroundColor: "rgba(21,128,61,0.1)", fill: true, tension: 0.3 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: -3.5, max: 0.5 } } }
  });
}

// =========================================================
// RECIPE BANK & A5 PDF GENERATOR
// =========================================================
function renderRecipeBank() {
  const climate = document.getElementById("recipe-climate-filter").value;
  const goal = document.getElementById("recipe-goal-filter").value;
  const scale = parseInt(document.getElementById("recipe-scale-select").value);
  const grid = document.getElementById("recipe-cards-grid");

  const filtered = appState.recipes.filter(r =>
    (climate === "All" || r.climate === climate) &&
    (goal === "All" || r.goal === goal)
  );

  grid.innerHTML = filtered.map(r => `
    <div class="recipe-card lift-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="tag">${r.region}</span>
        <span class="badge-jan">${scale === 1 ? "1 Child" : "25 Kids Batch"}</span>
      </div>
      <h4 style="margin:8px 0 4px; color:#1e3a8a; font-size:1.05rem;">${r.name}</h4>
      <div class="recipe-meta">
        <span class="tag">💰 ₹${(r.cost * scale).toFixed(2)} total</span>
        <span class="tag">🔥 ${r.kcal} kcal/child</span>
        <span class="tag">💪 ${r.protein}g protein/child</span>
      </div>
      <details class="recipe-drawer" open>
        <summary>📖 Ingredients (${scale === 1 ? "1 Child" : "25-Child Batch"}) & Method</summary>
        <ul>${r.ingredients.map(i => `<li><b>${i.qty * scale} ${i.unit}</b> ${i.item}</li>`).join("")}</ul>
        <ol>${r.steps.map(s => `<li>${s}</li>`).join("")}</ol>
      </details>
    </div>
  `).join("");
}

function populatePDFChildDropdown() {
  const sel = document.getElementById("pdf-child-select");
  sel.innerHTML = appState.children.map((c, idx) =>
    `<option value="${idx}">${c.name} (${c.age}m • ${c.status} • ${c.city}, ${c.state})</option>`
  ).join("");
}

function renderHealthCardPreview() {
  const sel = document.getElementById("pdf-child-select");
  const child = appState.children[sel.value || 0] || appState.children[0];
  if (!child) return;
  const staples = appState.stateStaples[child.state] || "Local Millets, Pulses & Greens";

  document.getElementById("health-card-preview").innerHTML = `
    <div style="border:2px solid #1e3a8a; border-radius:12px; overflow:hidden;">
      <div style="background:#ea580c; color:#fff; padding:12px 16px; font-weight:800;">
        🇮🇳 POSHANDRISHTI — CHILD HEALTH CARD ("Sahi Poshan, Bachpan Roshan")
      </div>
      <div style="padding:14px 16px; font-size:0.9rem; line-height:1.7;">
        <div><b>Child Name:</b> ${child.name} &nbsp;|&nbsp; <b>Age/Gender:</b> ${child.age} Months (${child.gender})</div>
        <div><b>Location:</b> ${child.city}, ${child.state}</div>
        <div><b>WHO Triage Status:</b> <span class="status-badge status-${child.status}">${child.status} (Z-Score: ${child.zScore})</span></div>
        <div><b>Clinical Note:</b> ${child.condition}</div>
        <div><b>Daily ICDS Meal Allocation:</b> ${child.cost} / day</div>
        <hr style="margin:10px 0; border-color:#e2e8f0;">
        <div><b>Regional Staples:</b> ${staples}</div>
      </div>
    </div>
  `;
}

function downloadChildHealthCardPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ format: "a5", orientation: "portrait" });
  const sel = document.getElementById("pdf-child-select");
  const child = appState.children[sel.value || 0] || appState.children[0];
  const staples = appState.stateStaples[child.state] || "Local Millets, Pulses & Greens";

  doc.setFillColor(234, 88, 12);
  doc.rect(0, 0, 148, 26, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(13);
  doc.setFont("helvetica", "bold");
  doc.text("POSHANDRISHTI - ANGANWADI HEALTH CARD", 10, 11);
  doc.setFontSize(9);
  doc.text("Sahi Poshan, Bachpan Roshan | Child Nutrition Portal (0-6 Yrs)", 10, 19);

  doc.setTextColor(15, 23, 42);
  doc.setFontSize(10);
  doc.text(`Child Name: ${child.name}`, 12, 38);
  doc.text(`Age & Gender: ${child.age} Months | ${child.gender}`, 12, 46);
  doc.text(`Location: ${child.city}, ${child.state}`, 12, 54);
  doc.text(`WHO Growth Status: ${child.status} (Z-Score: ${child.zScore})`, 12, 62);
  doc.text(`Daily Meal Budget: ${child.cost} / day`, 12, 70);

  doc.setDrawColor(30, 58, 138);
  doc.line(12, 76, 136, 76);

  doc.setFont("helvetica", "bold");
  doc.text("Recommended Regional Staples:", 12, 85);
  doc.setFont("helvetica", "normal");
  doc.text(doc.splitTextToSize(staples, 122), 12, 92);

  doc.setFont("helvetica", "bold");
  doc.text("Caregiver & Anganwadi Feeding Protocol:", 12, 108);
  doc.setFont("helvetica", "normal");
  const advice = child.status === "SAM"
    ? "CRITICAL SAM CARE: Provide 6 small calorie-dense meals daily enriched with 2 tsp ghee/oil and THR peanut-jaggery laddu. Attend weekly VHSND weigh-ins."
    : child.status === "MAM"
    ? "MAM RECOVERY: Fortify daily Hot Cooked Meal with 1 boiled egg or 20g roasted chana/sattu powder and moringa leaves."
    : "HEALTHY GROWTH: Continue daily ICDS Hot Cooked Meal, seasonal fruits, and safe drinking water.";
  doc.text(doc.splitTextToSize(advice, 122), 12, 115);

  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.text("Anganwadi Worker Signature: ______________________", 12, 185);
  doc.text("Poshan Helpline: 14408 | Childline: 1098", 12, 195);

  doc.save(`PoshanDrishti_Card_${child.name.replace(/\s+/g, "_")}.pdf`);
}

window.addEventListener("DOMContentLoaded", loadBackendBootstrap);
