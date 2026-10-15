# Giai đoạn 1: Build file WAR bằng Maven
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Giai đoạn 2: Chạy ứng dụng bằng file WAR (đổi sang Java 17 vì pom.xml của bạn đang khai báo java.version là 17)
FROM eclipse-temurin:17-jre
WORKDIR /app
# Sao chép file .war được build ra trong thư mục target thành app.war
COPY --from=build /app/target/*.war app.war

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.war"]