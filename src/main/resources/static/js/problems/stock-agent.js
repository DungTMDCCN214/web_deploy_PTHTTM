document.addEventListener("DOMContentLoaded", () => {
  const questionInput = document.getElementById("agentQuestion");
  const askBtn = document.getElementById("askAgentBtn");
  const errorBox = document.getElementById("agentError");
  const asOfLabel = document.getElementById("stockAsOf");
  const metricsBox = document.getElementById("stockMetrics");
  const forecastSummary = document.getElementById("forecastSummary");
  const traceBox = document.getElementById("agentTrace");
  const kgSeeds = document.getElementById("stockKgSeeds");
  const kgFacts = document.getElementById("stockKgFacts");
  const ragHits = document.getElementById("stockRagHits");
  const reportSummary = document.getElementById("agentReportSummary");
  const reportSections = document.getElementById("agentReportSections");
  const disclaimer = document.getElementById("agentDisclaimer");
  const canvas = document.getElementById("stockChart");
  const ctx = canvas.getContext("2d");

  let historyPrices = [];

  const money = (value) => `${Number(value || 0).toFixed(2)} USD`;

  const renderTags = (container, items) => {
    container.innerHTML = "";
    (items || []).forEach((item) => {
      const tag = document.createElement("span");
      tag.className = "rag-tag";
      tag.textContent = item;
      container.appendChild(tag);
    });
  };

  const drawChart = (forecast) => {
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--surface") || "#fff";
    ctx.fillRect(0, 0, width, height);

    const hist = historyPrices.map((p) => ({ date: p.date, close: p.close, kind: "history" }));
    const fut = forecast ? forecast.forecast.map((p) => ({ date: p.date, close: p.forecast_close, lower: p.lower, upper: p.upper, kind: "forecast" })) : [];
    const points = hist.concat(fut);
    if (points.length < 2) {
      ctx.fillStyle = "#5b6b82";
      ctx.fillText("Không có dữ liệu biểu đồ.", 24, 32);
      return;
    }

    const values = points.flatMap((p) => [p.close, p.lower, p.upper].filter((v) => Number.isFinite(v)));
    const min = Math.min(...values);
    const max = Math.max(...values);
    const pad = 36;
    const x = (i) => pad + (i / (points.length - 1)) * (width - pad * 2);
    const y = (v) => height - pad - ((v - min) / (max - min || 1)) * (height - pad * 2);

    ctx.strokeStyle = "#d9e0e8";
    ctx.lineWidth = 1;
    for (let i = 0; i < 4; i += 1) {
      const yy = pad + i * ((height - pad * 2) / 3);
      ctx.beginPath();
      ctx.moveTo(pad, yy);
      ctx.lineTo(width - pad, yy);
      ctx.stroke();
    }

    if (fut.length) {
      const start = hist.length;
      ctx.fillStyle = "rgba(240, 162, 59, .18)";
      ctx.beginPath();
      fut.forEach((p, idx) => {
        const xx = x(start + idx);
        const yy = y(p.upper);
        if (idx === 0) ctx.moveTo(xx, yy); else ctx.lineTo(xx, yy);
      });
      [...fut].reverse().forEach((p, idx) => {
        ctx.lineTo(x(start + fut.length - 1 - idx), y(p.lower));
      });
      ctx.closePath();
      ctx.fill();
    }

    ctx.strokeStyle = "#07695d";
    ctx.lineWidth = 2;
    ctx.beginPath();
    hist.forEach((p, idx) => {
      if (idx === 0) ctx.moveTo(x(idx), y(p.close)); else ctx.lineTo(x(idx), y(p.close));
    });
    ctx.stroke();

    if (fut.length) {
      ctx.strokeStyle = "#d92d20";
      ctx.setLineDash([6, 5]);
      ctx.beginPath();
      const lastHist = hist[hist.length - 1];
      ctx.moveTo(x(hist.length - 1), y(lastHist.close));
      fut.forEach((p, idx) => ctx.lineTo(x(hist.length + idx), y(p.close)));
      ctx.stroke();
      ctx.setLineDash([]);
    }

    ctx.fillStyle = "#5b6b82";
    ctx.font = "12px sans-serif";
    ctx.fillText(`${money(max)}`, 8, pad + 4);
    ctx.fillText(`${money(min)}`, 8, height - pad);
    ctx.fillText(points[0].date, pad, height - 10);
    ctx.fillText(points[points.length - 1].date, width - 120, height - 10);
  };

  const renderMetrics = (modelInfo) => {
    const models = modelInfo.metrics && modelInfo.metrics.models ? modelInfo.metrics.models : {};
    const rows = [
      ["LSTM RMSE", models.lstm_demo && models.lstm_demo.rmse],
      ["GRU RMSE", models.gru_demo && models.gru_demo.rmse],
      ["Naive RMSE", models.naive_persistence && models.naive_persistence.rmse],
      ["Naive MAPE", models.naive_persistence && `${models.naive_persistence.mape}%`],
      ["Rows", modelInfo.rows],
      ["AS OF", modelInfo.as_of_date],
    ];
    metricsBox.innerHTML = rows.map(([label, value]) => `<div><strong>${value || "--"}</strong><span>${label}</span></div>`).join("");
  };

  const loadInitial = async () => {
    const [infoRes, pricesRes] = await Promise.all([
      fetch("/api/stock-agent/model-info"),
      fetch("/api/stock-agent/prices?start=2019-09-23&end=2020-09-23"),
    ]);
    const info = await infoRes.json();
    const prices = await pricesRes.json();
    asOfLabel.textContent = `Mốc dữ liệu: ${info.as_of_date} · ${info.start_date} đến ${info.end_date}`;
    renderMetrics(info);
    historyPrices = prices.prices || [];
    drawChart(null);
  };

  const renderAgent = (data) => {
    const forecast = data.forecast;
    if (forecast) {
      forecastSummary.textContent = `Đóng cửa ${forecast.as_of_date}: ${money(forecast.last_close)}. Dự báo cuối kỳ: ${money(forecast.forecast.at(-1).forecast_close)} (${forecast.direction}).`;
      drawChart(forecast);
    } else {
      forecastSummary.textContent = "Không có dự báo cho câu hỏi ngoài phạm vi.";
      drawChart(null);
    }

    traceBox.innerHTML = (data.trace || []).map((step) => `<li><strong>${step.tool}</strong> · ${step.status} · ${step.elapsed_ms}ms<br><span>${step.detail}</span></li>`).join("");
    renderTags(kgSeeds, data.kg_seeds || []);
    kgFacts.textContent = (data.kg_facts || []).map(([s, r, o]) => `(${s}, ${r}, ${o})`).join("\n") || "Không có fact phù hợp.";

    const hits = data.rag_hits || [];
    ragHits.innerHTML = hits.length
      ? hits.map((hit) => `<article class="rag-hit"><strong>${hit.source} · ${hit.doc_type} · trang ${hit.page} · ${hit.date} · score ${hit.score}</strong><p>${hit.text}</p></article>`).join("")
      : "Cơ sở tri thức không có đủ thông tin.";

    const report = data.report || {};
    reportSummary.textContent = report.summary || "Không có báo cáo.";
    reportSections.innerHTML = (report.sections || []).map((section) => `<li>${section}</li>`).join("");
    disclaimer.textContent = report.disclaimer || data.disclaimer || disclaimer.textContent;
  };

  const askAgent = async () => {
    errorBox.hidden = true;
    askBtn.disabled = true;
    askBtn.textContent = "Đang chạy...";
    try {
      const response = await fetch("/api/stock-agent/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: questionInput.value, session_id: "demo-web", as_of_date: "2020-09-23", horizon: 5 }),
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.message || "Tác tử không phản hồi thành công.");
      }
      renderAgent(data);
    } catch (error) {
      errorBox.hidden = false;
      errorBox.textContent = error.message;
    } finally {
      askBtn.disabled = false;
      askBtn.textContent = "Gửi tác tử";
    }
  };

  document.querySelectorAll(".sample-question").forEach((button) => {
    button.addEventListener("click", () => {
      questionInput.value = button.dataset.question;
    });
  });
  askBtn.addEventListener("click", askAgent);

  loadInitial().then(askAgent).catch((error) => {
    errorBox.hidden = false;
    errorBox.textContent = error.message;
  });
});
