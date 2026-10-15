# AI & Deep Learning Studio (khung Spring Boot + JSP)

## Chạy
Yêu cầu: JDK 17+, Maven.

    mvn spring-boot:run

Mở http://localhost:8080

## Cấu trúc
- `service/ProblemRegistry.java`  danh sách bài toán, menu tự sinh từ đây
- `controller/PageController`      `/` (menu) và `/problem/{id}` (trang demo)
- `controller/ApiController`       `POST /api/{id}/predict` (hiện trả dữ liệu giả)
- `WEB-INF/views/problems/{id}.jsp` giao diện riêng từng bài
- `static/js/problems/{id}.js`     JS riêng từng bài
- `static/css/style.css`, `static/js/app.js`  dùng chung

## Thêm một bài mới
1. Thêm 1 dòng `new Problem(...)` vào `ProblemRegistry`.
2. Tạo `problems/{id}.jsp` và `static/js/problems/{id}.js`.
3. (Tùy chọn) tạo controller riêng cho `/api/{id}/...` thay cho `ApiController`.
