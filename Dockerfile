# Giai đoạn 1: Build file JAR bằng Maven (sử dụng nền tảng Java 21 tương thích)
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Chạy ứng dụng Spring Boot
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

# Render tự động gán cổng qua biến môi trường PORT hoặc mặc định là 8080
ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]