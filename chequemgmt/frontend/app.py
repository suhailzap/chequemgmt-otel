from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
import requests
import os

app = Flask(__name__)

# Configure logging to output to stdout (best practice for Docker/Kubernetes)
logging.basicConfig(
    format='%(levelname)s:%(name)s:%(module)s:%(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Default backend URL (can be overridden by the BACKEND_URL environment variable)
# Best practice: use internal service names if running in K8s/Docker Compose
app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8085/cheques')

# ---------------------------------------------------------
# NEW: HEALTH CHECK ENDPOINT
# Required for CI/CD pipeline health checks and K8s Probes
# ---------------------------------------------------------
@app.route('/health')
def health_check():
    """
    Returns a 200 OK status to indicate the container is alive.
    Used by the GitHub Action 'Test Docker image' step.
    """
    return jsonify({"status": "healthy", "container": "frontend"}), 200

@app.route('/')
def index():
    backend_url = app.config['BACKEND_URL'] + '/list'
    cheque_data = []
    
    try:
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            logger.info("GET %s - OK", backend_url)
            cheque_data = response.json()
        else:
            logger.error("GET %s - FAILED with status %s", backend_url, response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("Backend unreachable at %s: %s", backend_url, str(e))

    return render_template('index.html', cheque_data=cheque_data)

@app.route('/add', methods=['POST'])
def add():
    chequeNo = request.form.get('chequeNo')
    approvalGranted = 'true' in request.form.getlist('approvalGranted')
    payload = {'chequeNo': chequeNo, 'approvalGranted': approvalGranted}
    
    backend_url = app.config['BACKEND_URL'] + '/add'
    logger.info("POST %s with payload %s", backend_url, payload)
    
    try:
        response = requests.post(backend_url, params=payload, timeout=5)
        if response.status_code != 200:
            logger.error("Failed to add new cheque details: %s", response.text)
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with backend: %s", str(e))
        
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    chequeNo = request.form.get('chequeNo')
    backend_url = app.config['BACKEND_URL'] + '/remove'
    
    logger.info("DELETE (POST-mapped) %s for chequeNo: %s", backend_url, chequeNo)
    
    try:
        # Note: Using data= to send as form-encoded, matching your previous logic
        response = requests.post(backend_url, data={'chequeNo': chequeNo}, timeout=5)
        if response.status_code != 200:
            logger.error("Failed to delete cheque data for cheque no %s: %s", chequeNo, response.text)
    except requests.exceptions.RequestException as e:
        logger.error("Error communicating with backend: %s", str(e))

    return redirect(url_for('index'))

if __name__ == '__main__':
    # host='0.0.0.0' is required for the container to be reachable
    app.run(host='0.0.0.0', port=5000)




















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
