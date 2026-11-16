# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119): build Portal BFF từ mã nguồn bằng Gradle 8.14.3 bên ngoài, chạy non-root.
FROM gradle:8.14.3-jdk21 AS build
WORKDIR /home/gradle
COPY --chown=gradle:gradle portal-bff/ portal-bff/
RUN gradle --version | grep -F 'Gradle 8.14.3' \
 && gradle --no-daemon -p portal-bff bootJar -x test \
 && cp "$(ls portal-bff/build/libs/*.jar | grep -v -- '-plain.jar' | head -n1)" /app.jar

FROM eclipse-temurin:21-jre
COPY --from=build --chown=10001:10001 /app.jar /app/application.jar
USER 10001:10001
ENTRYPOINT ["java", "-jar", "/app/application.jar"]
