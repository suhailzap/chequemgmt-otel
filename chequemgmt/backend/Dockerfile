########################
# STAGE 1: Dependency Cache
########################
FROM maven:3.9.6-eclipse-temurin-21 AS deps
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline

########################
# STAGE 2: Build Application
########################
FROM deps AS builder
COPY src ./src
RUN mvn clean package -DskipTests

########################
# STAGE 3: Final Runtime
########################
FROM eclipse-temurin:21-jre-alpine AS runtime

# Security Hardening: Update existing packages and add non-root user
RUN apk update && apk upgrade && \
    adduser -D appuser && \
    rm -rf /var/cache/apk/*

WORKDIR /app

# Download OTel Agent
# ARG OTEL_VERSION=2.7.0
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar /app/opentelemetry-javaagent.jar
# ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_VERSION}/opentelemetry-javaagent.jar .

# Copy only the final artifact from builder stage
COPY --from=builder /build/target/chequebackend-0.0.1-SNAPSHOT.jar app.jar

RUN chown appuser:appuser /app/app.jar /app/opentelemetry-javaagent.jar

USER appuser

# OTel Configuration
ENV OTEL_SERVICE_NAME=java-backend-service \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
    OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
    OTEL_TRACES_SAMPLER=always_on \
    OTEL_LOGS_EXPORTER=otlp \
    OTEL_METRICS_EXPORTER=none

EXPOSE 8085

ENTRYPOINT ["java", "-javaagent:/app/opentelemetry-javaagent.jar", "-jar", "/app/app.jar"]
