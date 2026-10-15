<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<div class="container my-4">
    <h2>Dự báo nguy cơ Bệnh Tiểu Đường</h2>
    <p class="text-muted">Nhập các thông số sinh lý để đánh giá mức độ nguy cơ tiểu đường.</p>

    <div class="row">
        <!-- Form nhập liệu -->
        <div class="col-md-6">
            <form id="diabetesForm">
                <div class="mb-3">
                    <label class="form-label">Chỉ số Glucose (mg/dL)</label>
                    <input type="number" step="any" class="form-control" name="glucose" required value="120">
                </div>
                <div class="mb-3">
                    <label class="form-label">Chỉ số BMI (kg/m²)</label>
                    <input type="number" step="any" class="form-control" name="bmi" required value="24.5">
                </div>
                <div class="mb-3">
                    <label class="form-label">Tuổi</label>
                    <input type="number" class="form-control" name="age" required value="30">
                </div>
                <div class="mb-3">
                    <label class="form-label">Huyết áp (Blood Pressure - mmHg)</label>
                    <input type="number" step="any" class="form-control" name="bloodPressure" value="70">
                </div>
                <div class="mb-3">
                    <label class="form-label">Số lần mang thai (Pregnancies)</label>
                    <input type="number" class="form-control" name="pregnancies" value="0">
                </div>
                <button type="submit" class="btn btn-primary">Dự đoán nguy cơ</button>
            </form>
        </div>

        <!-- Khung hiển thị kết quả -->
        <div class="col-md-6">
            <div id="resultCard" class="card d-none">
                <div class="card-header bg-primary text-white">Kết quả dự báo</div>
                <div class="card-body">
                    <h4 id="riskLevel" class="card-title">--</h4>
                    <p>Xác suất nguy cơ: <strong id="probability">0%</strong></p>
                    <div class="alert alert-info" id="advice">--</div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="/js/problems/diabetes.js"></script>