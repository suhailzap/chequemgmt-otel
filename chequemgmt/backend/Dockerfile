FROM eclipse-temurin:21-jre

WORKDIR /app

# Download OpenTelemetry Java Agent
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar /app/opentelemetry-javaagent.jar

# Copy application JAR
COPY target/chequebackend-0.0.1-SNAPSHOT.jar /app/app.jar

# OpenTelemetry configuration
ENV OTEL_SERVICE_NAME=java-backend-service
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV OTEL_TRACES_SAMPLER=always_on

# IMPORTANT: enable logs
ENV OTEL_LOGS_EXPORTER=otlp

# Disable metrics explicitly
ENV OTEL_METRICS_EXPORTER=none

EXPOSE 8085

ENTRYPOINT ["java", "-javaagent:/app/opentelemetry-javaagent.jar", "-jar", "/app/app.jar"]
