<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>
<div class="split">
  <div class="panel">
    <h2>Đầu vào</h2>
    <%-- TODO: thay bằng form thật của bài "mnist" (input, slider, canvas, webcam...) --%>
    <label for="input">Dữ liệu thử (JSON)</label>
    <textarea id="input" rows="6">{ "example": 1 }</textarea>
    <button id="run" class="btn">Chạy thử</button>
  </div>
  <div class="panel">
    <h2>Kết quả</h2>
    <pre id="result" class="result">Nhập dữ liệu và bấm "Chạy thử".</pre>
  </div>
</div>
