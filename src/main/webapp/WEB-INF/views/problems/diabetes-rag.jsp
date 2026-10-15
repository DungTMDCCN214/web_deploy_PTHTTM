<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>

<section class="rag-demo">
  <div class="rag-grid rag-top">
    <form id="diabetesRagForm" class="panel rag-form">
      <h2>Nhập 8 chỉ số lâm sàng</h2>
      <div class="rag-input-grid">
        <label>Pregnancies
          <input name="pregnancies" type="number" step="1" value="1" min="0" max="20">
        </label>
        <label>Glucose (mg/dL)
          <input name="glucose" type="number" step="any" value="92" min="0" max="300">
        </label>
        <label>Blood Pressure (mmHg)
          <input name="bloodPressure" type="number" step="any" value="66" min="0" max="200">
        </label>
        <label>Skin Thickness (mm)
          <input name="skinThickness" type="number" step="any" value="23" min="0" max="100">
        </label>
        <label>Insulin
          <input name="insulin" type="number" step="any" value="94" min="0" max="1000">
        </label>
        <label>BMI (kg/m²)
          <input name="bmi" type="number" step="any" value="24.5" min="0" max="80">
        </label>
        <label>Diabetes Pedigree Function
          <input name="diabetesPedigreeFunction" type="number" step="any" value="0.25" min="0" max="3">
        </label>
        <label>Age
          <input name="age" type="number" step="1" value="24" min="1" max="120">
        </label>
      </div>
      <div class="rag-actions">
        <button class="btn" type="submit">Phân tích</button>
        <button class="btn btn-secondary" type="button" id="lowSampleBtn">Mẫu nguy cơ thấp</button>
        <button class="btn btn-secondary" type="button" id="highSampleBtn">Mẫu nguy cơ cao</button>
      </div>
      <p id="ragError" class="rag-error" hidden></p>
    </form>

    <section class="panel rag-result-card">
      <h2>Deep Learning</h2>
      <div id="riskPercent" class="risk-percent">--%</div>
      <div class="risk-bar">
        <span id="riskBarFill"></span>
      </div>
      <div id="riskBadge" class="risk-badge">Chưa phân tích</div>
      <div id="modelMetrics" class="metric-grid"></div>
      <p class="rag-note">Hiệu năng này chỉ phục vụ demo học tập, chưa đủ dùng lâm sàng.</p>
    </section>
  </div>

  <div class="rag-grid">
    <section class="panel">
      <h2>Knowledge Graph</h2>
      <div id="kgSeeds" class="tag-row"></div>
      <pre id="kgFacts" class="kg-facts">Chưa có dữ liệu.</pre>
    </section>

    <section class="panel">
      <h2>RAG Evidence</h2>
      <div id="ragHits" class="rag-hit-list">Chưa có bằng chứng.</div>
    </section>
  </div>

  <section class="panel rag-report-panel">
    <h2>Báo cáo tổng hợp</h2>
    <div id="preprocessNotes" class="tag-row"></div>
    <ol id="fusionReport" class="fusion-report">
      <li>Nhập dữ liệu và bấm Phân tích để xem báo cáo.</li>
    </ol>
    <p id="ragDisclaimer" class="disclaimer">Kết quả chỉ phục vụ học tập; không thay thế chẩn đoán của bác sĩ.</p>
  </section>
</section>
