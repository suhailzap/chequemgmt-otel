FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copy dependency file first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install \
      opentelemetry-api \
      opentelemetry-sdk \
      opentelemetry-exporter-otlp \
      opentelemetry-instrumentation-flask \
      opentelemetry-instrumentation-requests \
      opentelemetry-distro && \
    opentelemetry-bootstrap -a install

# Copy application source
COPY . .

ENV OTEL_SERVICE_NAME=frontend-service
# === TRACES (gRPC on 4317) ===
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=grpc://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=grpc
ENV OTEL_TRACES_SAMPLER=always_on
# === METRICS (HTTP on 4318) ===
ENV OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://otel-collector:4318/v1/metrics
ENV OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
ENV OTEL_METRICS_EXPORTER=otlp
# === LOGS (HTTP on 4318) ===
ENV OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://otel-collector:4318/v1/logs
ENV OTEL_EXPORTER_OTLP_LOGS_PROTOCOL=http/protobuf
ENV OTEL_LOGS_EXPORTER=otlp
# === GENERAL ===
ENV OTEL_EXPORTER_OTLP_INSECURE=true
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

# # OpenTelemetry configuration
# ENV OTEL_SERVICE_NAME=frontend-service
# ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
# ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc, http
# ENV OTEL_EXPORTER_OTLP_INSECURE=true
# ENV OTEL_TRACES_SAMPLER=always_on

# # IMPORTANT: enable logs
# ENV OTEL_LOGS_EXPORTER=otlp
# ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

# # Disable metrics
# ENV OTEL_METRICS_EXPORTER=otlp

EXPOSE 5000

CMD ["opentelemetry-instrument", "python", "app.py"]
