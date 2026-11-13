# Spike D1 (#119): build backend từ mã nguồn.
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY backend/ ./
RUN chmod +x gradlew && ./gradlew --no-daemon bootJar -x test \
 && cp "$(ls build/libs/*.jar | grep -v -- '-plain.jar' | head -n1)" /app.jar

FROM eclipse-temurin:21-jre
COPY --from=build --chown=10001:10001 /app.jar /app/application.jar
USER 10001:10001
ENTRYPOINT ["java", "-jar", "/app/application.jar"]
