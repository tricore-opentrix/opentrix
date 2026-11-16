# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119): build backend từ mã nguồn bên trong Docker, chạy non-root.
FROM gradle:8.14.3-jdk21 AS build
WORKDIR /home/gradle
COPY --chown=gradle:gradle backend/ backend/
RUN gradle --version | grep -F 'Gradle 8.14.3' \
 && gradle -p backend --no-daemon bootJar -x test \
 && cp "$(ls backend/build/libs/*.jar | grep -v -- '-plain.jar' | head -n1)" /app.jar

FROM eclipse-temurin:21-jre
COPY --from=build --chown=10001:10001 /app.jar /app/application.jar
USER 10001:10001
ENTRYPOINT ["java", "-jar", "/app/application.jar"]
