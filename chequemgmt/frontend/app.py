from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
import requests
import os

app = Flask(__name__)
logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(name)s:%(module)s:%(message)s', level=logging.INFO)

# Default backend URL (can be overridden by the BACKEND_URL environment variable)
app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8085/cheques')

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

    return render_template('index.html', cheque_data=cheque_data)

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        chequeNo = request.form['chequeNo']
        approvalGranted = 'true' in request.form.getlist('approvalGranted')
        payload = {'chequeNo': chequeNo, 'approvalGranted': approvalGranted}
        backend_url = app.config['BACKEND_URL'] + '/add'
        logging.info("POST %s with payload %s", backend_url, payload)
        response = requests.post(backend_url, params=payload)
        if response.status_code != 200:
            logging.error("Failed to add new cheque details: %s", response.text)
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        chequeNo = request.form['chequeNo']
        backend_url = app.config['BACKEND_URL'] + f'/remove'
        logging.info("DELETE %s", backend_url)
        response = requests.post(backend_url, data={'chequeNo': chequeNo})
        if response.status_code != 200:
            logging.error("Failed to delete cheque data for cheque no %s: %s", chequeNo, response.text)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')