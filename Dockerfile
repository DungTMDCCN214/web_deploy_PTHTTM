# Giai đoạn 1: Build file WAR bằng Maven
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Cài đặt môi trường chạy chứa cả Java (cho Spring Boot) và Python (cho các model AI)
FROM eclipse-temurin:17-jre

# Cài đặt Python 3, pip và các công cụ hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Sao chép file WAR đã build từ giai đoạn 1
COPY --from=build /app/target/*.war app.war

# Sao chép toàn bộ thư mục chứa mã nguồn python và mô hình AI sang container chạy
COPY --from=build /app/ml_models /app/ml_models

# Cài đặt các thư viện Python (nếu bạn có file requirements.txt, có thể chạy pip install, hoặc cài trực tiếp các thư viện phổ biến)
# RUN pip3 install --no-cache-dir numpy pandas scikit-learn tensorflow torch

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.war"]