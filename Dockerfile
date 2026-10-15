# Giai đoạn 1: Build file JAR bằng Maven
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Chạy ứng dụng Spring Boot
FROM eclipse-temurin:21-jre
WORKDIR /app
# Dùng lệnh sao chép linh hoạt để không bị phụ thuộc vào tên file jar cụ thể
COPY --from=build /app/target/*.jar app.jar

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]