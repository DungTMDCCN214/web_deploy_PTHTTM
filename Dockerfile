# Giai đoạn 1: Build file WAR bằng Maven
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Môi trường chạy chứa Java 17 và Python 3 đầy đủ thư viện AI
FROM eclipse-temurin:17-jre

# Cài đặt Python 3, pip và các công cụ biên dịch cần thiết
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt sẵn các thư viện Python cho mô hình ML/AI (vượt rào PEP 668 cho Ubuntu/Debian mới)
RUN pip3 install --no-cache-dir --break-system-packages numpy pandas scikit-learn joblib

WORKDIR /app

# Sao chép file WAR và thư mục chứa mô hình AI từ giai đoạn build
COPY --from=build /app/target/*.war app.war
COPY --from=build /app/ml_models /app/ml_models

ENV PORT=8080
EXPOSE 8080

# Chạy dưới dạng shell form để Tomcat nhận chính xác biến môi trường PORT từ Render và tối ưu SecureRandom
ENTRYPOINT java -Djava.security.egd=file:/dev/./urandom -Dserver.port=${PORT} -Dserver.address=0.0.0.0 -jar app.war