FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (layer caching)
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

# OpenTelemetry environment variables
ENV OTEL_PYTHON_AUTO_INSTRUMENTATION_ENABLED=true
ENV OTEL_EXPORTER_OTLP_INSECURE=true
ENV OTEL_TRACES_SAMPLER=always_on
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV OTEL_SERVICE_NAME=frontend-service
ENV OTEL_METRICS_EXPORTER=none

EXPOSE 5000

CMD ["opentelemetry-instrument", \
     "--traces_exporter", "otlp", \
     "--metrics_exporter", "none", \
     "python", "app.py"]
