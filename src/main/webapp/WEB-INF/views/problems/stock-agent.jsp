<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>

<section class="agent-demo">
  <section class="panel agent-ask">
    <div class="agent-head">
      <div>
        <h2>Tác tử tài chính AMZN</h2>
        <p id="stockAsOf">Mốc dữ liệu: đang tải...</p>
      </div>
      <span class="agent-pill">Không phải tư vấn đầu tư</span>
    </div>
    <label>Câu hỏi
      <textarea id="agentQuestion" rows="3">Dự báo giá cổ phiếu Amazon tuần tới và giải thích vai trò AWS gần đây?</textarea>
    </label>
    <div class="rag-actions">
      <button class="btn" id="askAgentBtn" type="button">Gửi tác tử</button>
      <button class="btn btn-secondary sample-question" type="button" data-question="Dự báo giá AMZN 5 phiên tới.">Mẫu dự báo</button>
      <button class="btn btn-secondary sample-question" type="button" data-question="AWS ảnh hưởng thế nào tới giá cổ phiếu Amazon?">Mẫu AWS</button>
      <button class="btn btn-secondary sample-question" type="button" data-question="Thời tiết Hà Nội tuần tới ra sao?">Ngoài phạm vi</button>
    </div>
    <p id="agentError" class="rag-error" hidden></p>
  </section>

  <div class="agent-grid">
    <section class="panel">
      <h2>Giá lịch sử và dự báo 5 phiên</h2>
      <canvas id="stockChart" class="stock-chart" width="900" height="360"></canvas>
      <div id="forecastSummary" class="agent-summary">Chưa có dự báo.</div>
    </section>

    <section class="panel">
      <h2>Đánh giá mô hình</h2>
      <div id="stockMetrics" class="metric-grid"></div>
      <p class="rag-note">Baseline naive: giá ngày mai = giá đóng cửa hôm nay. Forecast Tool hiện là demo log-return rolling.</p>
    </section>
  </div>

  <div class="agent-grid">
    <section class="panel">
      <h2>Quy trình tác tử</h2>
      <ol id="agentTrace" class="agent-trace">
        <li>Chưa chạy.</li>
      </ol>
    </section>

    <section class="panel">
      <h2>Knowledge Graph facts</h2>
      <div id="stockKgSeeds" class="tag-row"></div>
      <pre id="stockKgFacts" class="kg-facts">Chưa có dữ liệu.</pre>
    </section>
  </div>

  <section class="panel">
    <h2>RAG bằng chứng</h2>
    <div id="stockRagHits" class="rag-hit-list">Chưa có bằng chứng.</div>
  </section>

  <section class="panel rag-report-panel">
    <h2>Báo cáo tổng hợp</h2>
    <p id="agentReportSummary" class="agent-summary">Nhập câu hỏi và bấm Gửi tác tử.</p>
    <ol id="agentReportSections" class="fusion-report"></ol>
    <p id="agentDisclaimer" class="disclaimer">Kết quả chỉ phục vụ học tập, không phải tư vấn đầu tư.</p>
  </section>
</section>
