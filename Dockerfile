# Giai đoạn 1: Build file WAR bằng Maven
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Môi trường chạy Java 17 và Python 3 đầy đủ
FROM eclipse-temurin:17-jre

# Cài đặt Python 3, pip và các gói build thiết yếu
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python dùng cho các mô hình AI trong dự án
RUN pip3 install --no-cache-dir --break-system-packages \
    numpy \
    pandas \
    scikit-learn \
    joblib \
    torch \
    torchvision \
    transformers \
    requests

WORKDIR /app

# Sao chép file WAR và thư mục chứa mô hình AI từ giai đoạn build
COPY --from=build /app/target/*.war app.war
COPY --from=build /app/ml_models /app/ml_models

ENV PORT=10000
EXPOSE 10000

# Khởi động ứng dụng Spring Boot trỏ đúng cổng và địa chỉ mạng 0.0.0.0
ENTRYPOINT ["java", "-Dserver.port=${PORT}", "-Dserver.address=0.0.0.0", "-jar", "app.war"]