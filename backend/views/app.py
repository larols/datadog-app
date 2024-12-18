from flask import Flask, jsonify, request
from ddtrace import patch_all, patch
from datadog import statsd
import logging
import requests
import jsonpickle  # Import jsonpickle for testing deserialization vulnerability

# Patch all supported libraries for Datadog tracing
patch_all()
patch(logging=True)  # Enable tracing for logging

# Initialize the Flask app
app = Flask(__name__)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Initialize a visit counter
visit_count = 0

# Define external API URLs
EXTERNAL_API_URL_1 = 'https://jsonplaceholder.typicode.com/posts/1'
EXTERNAL_API_URL_2 = 'https://api.coindesk.com/v1/bpi/currentprice.json'

@app.route('/api/views', methods=['GET'])
def get_views_data():
    global visit_count
    visit_count += 1
    statsd.increment('custom.visits.count', 1)
    log.info(f"Visitor count: {visit_count}")
    data = {
        "id": 1,
        "text": f"You are visitor number {visit_count}!"
    }
    return jsonify(data)

@app.route('/api/visits', methods=['GET'])
def get_visit_count():
    log.info("Fetching visit count")
    return jsonify({"visit_count": visit_count})

@app.route('/api/external', methods=['GET'])
def fetch_external_data():
    try:
        response = requests.get(EXTERNAL_API_URL_1, timeout=5)
        response.raise_for_status()
        data = response.json()
        log.info("Successfully fetched external data from URL 1.")
        return jsonify({"message": "External data fetched successfully from URL 1", "data": data}), 200
    except requests.RequestException as e:
        log.error(f"Failed to fetch external data from URL 1: {e}")
        return jsonify({"error": "Failed to fetch external data"}), 500

@app.route('/api/external2', methods=['GET'])
def fetch_external_data2():
    try:
        response = requests.get(EXTERNAL_API_URL_2, timeout=5)
        response.raise_for_status()
        data = response.json()
        log.info("Successfully fetched external data from URL 2.")
        return jsonify({"message": "External data fetched successfully from URL 2", "data": data}), 200
    except requests.RequestException as e:
        log.error(f"Failed to fetch external data from URL 2: {e}")
        return jsonify({"error": "Failed to fetch external data"}), 500
    


# Route for testing jsonpickle deserialization vulnerability
@app.route('/api/deserialize', methods=['POST'])
def unsafe_deserialize():
    # Get the JSON payload and attempt to deserialize it using jsonpickle
    payload = request.get_data(as_text=True)
    try:
        deserialized_data = jsonpickle.decode(payload)
        log.info("Successfully deserialized data using jsonpickle.")
        return jsonify({"message": "Deserialization successful", "data": deserialized_data}), 200
    except Exception as e:
        log.error(f"Deserialization error: {e}")
        return jsonify({"error": "Failed to deserialize data"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
