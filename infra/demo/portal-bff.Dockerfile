# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119): build Portal BFF từ mã nguồn (dùng Gradle Wrapper của backend), chạy non-root.
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY backend/gradlew backend/gradlew
COPY backend/gradle backend/gradle
COPY portal-bff/ portal-bff/
RUN chmod +x backend/gradlew && ./backend/gradlew --no-daemon -p portal-bff bootJar -x test \
 && cp "$(ls portal-bff/build/libs/*.jar | grep -v -- '-plain.jar' | head -n1)" /app.jar

FROM eclipse-temurin:21-jre
COPY --from=build --chown=10001:10001 /app.jar /app/application.jar
USER 10001:10001
ENTRYPOINT ["java", "-jar", "/app/application.jar"]
