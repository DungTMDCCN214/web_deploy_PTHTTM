# ===== Giai đoạn 1: Build WAR bằng Maven =====
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B clean package -DskipTests

# ===== Giai đoạn 2: Java 17 + Python 3 =====
FROM eclipse-temurin:17-jre
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Chỉ cài thư viện mà các script thực sự dùng (không cần torch/transformers).
# scikit-learn phải đúng 1.7.2 vì diabetes_model.sav được train bằng bản này.
RUN pip3 install --no-cache-dir --break-system-packages \
        numpy pandas scikit-learn==1.7.2 joblib

WORKDIR /app
COPY --from=build /app/target/*.war app.war
COPY ml_models ./ml_models
# agent.py của stock_agent đọc CSV theo đường dẫn này nên phải copy vào image
COPY src/main/java/vn/ptit/aistudio/dto/chung_khoan/Chung_khoan.csv \
     ./src/main/java/vn/ptit/aistudio/dto/chung_khoan/Chung_khoan.csv

ENV PYTHON_CMD=python3 \
    PORT=10000 \
    JAVA_OPTS="-Xms128m -Xmx384m -XX:+UseSerialGC"
EXPOSE 10000

# Dạng shell để ${PORT} và ${JAVA_OPTS} được mở rộng; exec để Java nhận tín hiệu tắt
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -Dserver.port=${PORT} -Dserver.address=0.0.0.0 -jar app.war"]
