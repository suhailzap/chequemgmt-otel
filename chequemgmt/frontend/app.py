from flask import Flask, render_template, request, redirect, url_for, jsonify
import logging
import requests
import os

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# === OpenTelemetry imports ===
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

resource = Resource(attributes={"service.name": "flask-app"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

logging.basicConfig(format='%(levelname)s:%(name)s:%(module)s:%(message)s', level=logging.INFO)
app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8085/cheques')

REQUEST_COUNTER = Counter('flask_app_requests_total', 'Total HTTP requests processed', ['method', 'endpoint', 'http_status'])
ADD_CHEQUE_COUNTER = Counter('flask_app_add_cheque_total', 'Total number of cheques added successfully')
DELETE_CHEQUE_COUNTER = Counter('flask_app_delete_cheque_total', 'Total number of cheques deleted successfully')


@app.route('/health')
def health_check():
    """Health check for CI/CD and Kubernetes Probes"""
    return jsonify({
        "status": "healthy", 
        "container": "frontend",
        "backend_configured": app.config['BACKEND_URL']
    }), 200

@app.route('/')
def index():
    backend_url = app.config['BACKEND_URL'] + '/list'
    response = requests.get(backend_url)
    cheque_data = []

    if response.status_code == 200:
        logging.info("GET %s - OK", backend_url)
        cheque_data = response.json()
    else:
        logging.error("GET %s - FAILED with status %s", backend_url, response.status_code)

    REQUEST_COUNTER.labels(method='GET', endpoint='index', http_status=response.status_code).inc()
    return render_template('index.html', cheque_data=cheque_data)

@app.route('/add', methods=['POST'])
def add():
    chequeNo = request.form['chequeNo']
    approvalGranted = 'true' in request.form.getlist('approvalGranted')
    payload = {'chequeNo': chequeNo, 'approvalGranted': approvalGranted}
    backend_url = app.config['BACKEND_URL'] + '/add'
    logging.info("POST %s with payload %s", backend_url, payload)
    response = requests.post(backend_url, params=payload)

    if response.status_code == 200:
        ADD_CHEQUE_COUNTER.inc()
    else:
        logging.error("Failed to add new cheque details: %s", response.text)

    REQUEST_COUNTER.labels(method='POST', endpoint='add', http_status=response.status_code).inc()
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    chequeNo = request.form['chequeNo']
    backend_url = app.config['BACKEND_URL'] + f'/remove'
    logging.info("DELETE %s", backend_url)
    response = requests.post(backend_url, data={'chequeNo': chequeNo})

    if response.status_code == 200:
        DELETE_CHEQUE_COUNTER.inc()
    else:
        logging.error("Failed to delete cheque data for cheque no %s: %s", chequeNo, response.text)

    REQUEST_COUNTER.labels(method='POST', endpoint='delete', http_status=response.status_code).inc()
    return redirect(url_for('index'))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0')





# =======================================================
# ========================================================
# ========================================================
# from flask import Flask, render_template, request, jsonify, redirect, url_for
# import logging
# import requests
# import os
# from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

# # 1. Configure logging
# logging.basicConfig(
#     format='%(levelname)s:%(name)s:%(module)s:%(message)s', 
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # 2. Robust Configuration
# # This prevents KeyError by setting a default if the Environment Variable is missing
# app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8085/cheques').rstrip('/')

# # 3. Prometheus Metrics
# REQUEST_COUNT = Counter('frontend_page_views_total', 'Total number of views on index')

# # ---------------------------------------------------------
# # ROUTES
# # ---------------------------------------------------------

# @app.route('/health')
# def health_check():
#     """Health check for CI/CD and Kubernetes Probes"""
#     return jsonify({
#         "status": "healthy", 
#         "container": "frontend",
#         "backend_configured": app.config['BACKEND_URL']
#     }), 200

# @app.route('/')
# def index():
#     REQUEST_COUNT.inc()
#     backend_url = f"{app.config['BACKEND_URL']}/list"
#     cheque_data = []
    
#     try:
#         logger.info("Fetching cheques from: %s", backend_url)
#         response = requests.get(backend_url, timeout=5)
#         if response.status_code == 200:
#             cheque_data = response.json()
#         else:
#             logger.error("Backend returned status: %s", response.status_code)
#     except Exception as e:
#         logger.error("Error connecting to backend: %s", str(e))

#     return render_template('index.html', cheque_data=cheque_data)

# @app.route('/add', methods=['POST'])
# def add():
#     chequeNo = request.form.get('chequeNo')
#     approvalGranted = 'true' in request.form.getlist('approvalGranted')
#     payload = {'chequeNo': chequeNo, 'approvalGranted': approvalGranted}
    
#     backend_url = f"{app.config['BACKEND_URL']}/add"
    
#     try:
#         response = requests.post(backend_url, params=payload, timeout=5)
#         if response.status_code != 200:
#             logger.error("Failed to add cheque: %s", response.text)
#     except Exception as e:
#         logger.error("Error adding cheque: %s", str(e))
        
#     return redirect(url_for('index'))

# @app.route('/delete', methods=['POST'])
# def delete():
#     chequeNo = request.form.get('chequeNo')
#     backend_url = f"{app.config['BACKEND_URL']}/remove"
    
#     try:
#         response = requests.post(backend_url, data={'chequeNo': chequeNo}, timeout=5)
#         if response.status_code != 200:
#             logger.error("Failed to delete cheque: %s", response.text)
#     except Exception as e:
#         logger.error("Error deleting cheque: %s", str(e))

#     return redirect(url_for('index'))

# @app.route('/metrics')
# def metrics():
#     """Exposes application metrics for Prometheus scraping"""
#     return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# if __name__ == '__main__':
#     # Use environment variable for port or default to 5000
#     port = int(os.getenv('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)


# ++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++


# from flask import Flask, render_template, request, jsonify, redirect, url_for
# import logging
# import requests
# import os

# app = Flask(__name__)
# logging.getLogger(__name__)
# logging.basicConfig(format='%(levelname)s:%(name)s:%(module)s:%(message)s', level=logging.INFO)

# # Default backend URL (can be overridden by the BACKEND_URL environment variable)
# app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8085/cheques')

# @app.route('/')
# def index():
#     backend_url = app.config['BACKEND_URL'] + '/list'
#     response = requests.get(backend_url)
#     cheque_data = []

#     if response.status_code == 200:
#         logging.info("GET %s - OK", backend_url)
#         cheque_data = response.json()
#     else:
#         logging.error("GET %s - FAILED with status %s", backend_url, response.status_code)

#     return render_template('index.html', cheque_data=cheque_data)

# @app.route('/add', methods=['POST'])
# def add():
#     if request.method == 'POST':
#         chequeNo = request.form['chequeNo']
#         approvalGranted = 'true' in request.form.getlist('approvalGranted')
#         payload = {'chequeNo': chequeNo, 'approvalGranted': approvalGranted}
#         backend_url = app.config['BACKEND_URL'] + '/add'
#         logging.info("POST %s with payload %s", backend_url, payload)
#         response = requests.post(backend_url, params=payload)
#         if response.status_code != 200:
#             logging.error("Failed to add new cheque details: %s", response.text)
#     return redirect(url_for('index'))

# @app.route('/delete', methods=['POST'])
# def delete():
#     if request.method == 'POST':
#         chequeNo = request.form['chequeNo']
#         backend_url = app.config['BACKEND_URL'] + f'/remove'
#         logging.info("DELETE %s", backend_url)
#         response = requests.post(backend_url, data={'chequeNo': chequeNo})
#         if response.status_code != 200:
#             logging.error("Failed to delete cheque data for cheque no %s: %s", chequeNo, response.text)
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
