########################
# STAGE 1: Download OTel + App Jar
########################
FROM eclipse-temurin:21-jre-jammy AS builder

WORKDIR /build

# Download OpenTelemetry Java Agent (version pinned for reliability)
ARG OTEL_VERSION=2.7.0
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_VERSION}/opentelemetry-javaagent.jar /build/opentelemetry-javaagent.jar

# Copy application JAR
COPY target/chequebackend-0.0.1-SNAPSHOT.jar /build/app.jar


########################
# STAGE 2: Final Runtime Image
########################
FROM eclipse-temurin:21-jre-alpine AS runtime

# -------------------------------
# SECURITY HARDENING
# -------------------------------
RUN adduser -D appuser && \
    apk add --no-cache --upgrade \
    # Remove compilers, package managers, shells
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy artifacts from builder
COPY --from=builder /build/app.jar .
COPY --from=builder /build/opentelemetry-javaagent.jar .

# Run as non-root user
USER appuser

# -------------------------------
# OpenTelemetry config
# -------------------------------
ENV OTEL_SERVICE_NAME=java-backend-service \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
    OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
    OTEL_TRACES_SAMPLER=always_on \
    OTEL_LOGS_EXPORTER=otlp \
    OTEL_METRICS_EXPORTER=none

EXPOSE 8085

ENTRYPOINT ["java", \
  "-javaagent:/app/opentelemetry-javaagent.jar", \
  "-jar", "/app/app.jar"]
