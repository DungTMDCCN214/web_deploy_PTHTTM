document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("diabetesRagForm");
  const errorBox = document.getElementById("ragError");
  const riskPercent = document.getElementById("riskPercent");
  const riskBarFill = document.getElementById("riskBarFill");
  const riskBadge = document.getElementById("riskBadge");
  const modelMetrics = document.getElementById("modelMetrics");
  const kgSeeds = document.getElementById("kgSeeds");
  const kgFacts = document.getElementById("kgFacts");
  const ragHits = document.getElementById("ragHits");
  const fusionReport = document.getElementById("fusionReport");
  const preprocessNotes = document.getElementById("preprocessNotes");
  const disclaimer = document.getElementById("ragDisclaimer");

  const samples = {
    low: [1, 92, 66, 23, 94, 24.5, 0.25, 24],
    high: [6, 175, 92, 35, 0, 36.8, 0.9, 52],
  };

  const names = [
    "pregnancies",
    "glucose",
    "bloodPressure",
    "skinThickness",
    "insulin",
    "bmi",
    "diabetesPedigreeFunction",
    "age",
  ];

  const riskLabels = {
    thap: "Thấp",
    trung_binh: "Trung bình",
    cao: "Cao",
  };

  const parseNumber = (value) => {
    const parsed = Number.parseFloat((value || "").toString().replace(",", "."));
    return Number.isFinite(parsed) ? parsed : 0;
  };

  const setSample = (key) => {
    samples[key].forEach((value, index) => {
      form.elements[names[index]].value = value;
    });
  };

  const readPayload = () => {
    const payload = {};
    names.forEach((name) => {
      payload[name] = parseNumber(form.elements[name].value);
    });
    return payload;
  };

  const renderTags = (container, items, emptyText) => {
    container.innerHTML = "";
    if (!items || !items.length) {
      container.textContent = emptyText;
      return;
    }
    items.forEach((item) => {
      const tag = document.createElement("span");
      tag.className = "rag-tag";
      tag.textContent = item;
      container.appendChild(tag);
    });
  };

  const renderMetrics = (info) => {
    const metrics = info && info.metrics ? info.metrics : {};
    const rows = [
      ["Model", info && info.model_type ? info.model_type : "--"],
      ["Features", info && info.n_features ? info.n_features : "--"],
      ["Accuracy", metrics.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : "--"],
      ["AUC", metrics.auc ? metrics.auc.toFixed(2) : "--"],
      ["F1", metrics.f1 ? metrics.f1.toFixed(2) : "--"],
      ["Recall", metrics.recall ? metrics.recall.toFixed(2) : "--"],
    ];
    modelMetrics.innerHTML = rows
      .map(([label, value]) => `<div><strong>${value}</strong><span>${label}</span></div>`)
      .join("");
  };

  const renderResult = (data) => {
    if (data.error) {
      throw new Error(data.message || "Không phân tích được dữ liệu.");
    }

    const percent = Math.round((data.probability || 0) * 1000) / 10;
    const risk = data.risk_level || "thap";
    riskPercent.textContent = `${percent.toFixed(1)}%`;
    riskBarFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
    riskBarFill.dataset.risk = risk;
    riskBadge.textContent = `Mức nguy cơ: ${riskLabels[risk] || risk}`;
    riskBadge.dataset.risk = risk;

    renderMetrics(data.model_info);
    renderTags(kgSeeds, data.kg_seeds, "Không có seed.");
    kgFacts.textContent = (data.kg_facts || [])
      .map(([s, r, o]) => `(${s}, ${r}, ${o})`)
      .join("\n") || "Không có fact phù hợp.";

    const hits = data.rag_hits || [];
    ragHits.innerHTML = hits.length
      ? hits.map((hit) => `
          <article class="rag-hit">
            <strong>${hit.source} · trang ${hit.page} · score ${hit.score}</strong>
            <p>${hit.text}</p>
          </article>
        `).join("")
      : "Cơ sở tri thức không có đủ thông tin.";

    renderTags(preprocessNotes, data.preprocess_notes, "");
    const report = data.report || {};
    const reportRows = [
      report.prediction,
      report.findings,
      report.kg,
      report.rag,
      report.action,
    ].filter(Boolean);
    fusionReport.innerHTML = reportRows.map((row) => `<li>${row}</li>`).join("");
    disclaimer.textContent = report.disclaimer || disclaimer.textContent;
  };

  const analyze = async () => {
    errorBox.hidden = true;
    riskBadge.textContent = "Đang phân tích...";
    const response = await fetch("/api/diabetes-rag/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readPayload()),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || "Backend không phản hồi thành công.");
    }
    renderResult(data);
  };

  document.getElementById("lowSampleBtn").addEventListener("click", () => setSample("low"));
  document.getElementById("highSampleBtn").addEventListener("click", () => setSample("high"));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await analyze();
    } catch (error) {
      errorBox.hidden = false;
      errorBox.textContent = error.message;
      riskBadge.textContent = "Không phân tích được";
    }
  });

  analyze().catch((error) => {
    errorBox.hidden = false;
    errorBox.textContent = error.message;
  });
});
