from flask import Flask, jsonify
from ddtrace import patch_all, patch
from datadog import initialize, statsd  # Import Datadog statsd for custom metrics
import logging
import requests

# Initialize Datadog
options = {
    'api_key': 'YOUR_DATADOG_API_KEY',  # Replace with your API key
    'app_key': 'YOUR_DATADOG_APP_KEY'   # Optional: Replace with your app key
}
initialize(**options)

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

# Define an external API to simulate data fetching
EXTERNAL_API_URL = 'https://jsonplaceholder.typicode.com/posts/1'

@app.route('/api/views', methods=['GET'])
def get_views_data():
    global visit_count
    visit_count += 1  # Increment the visit counter

    # Send a custom metric to Datadog
    statsd.increment('custom.visits.count', 1)  # Increment the visit count metric

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
        # Make an external API call to get sample data
        response = requests.get(EXTERNAL_API_URL, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Parse the JSON response

        log.info("Successfully fetched external data.")
        return jsonify({"message": "External data fetched successfully", "data": data}), 200
    except requests.RequestException as e:
        log.error(f"Failed to fetch external data: {e}")
        return jsonify({"error": "Failed to fetch external data"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Expose the app on port 5000
