import os
import logging
import requests
from flask import Flask, jsonify
from kubernetes import client, config
import ddtrace

app = Flask(__name__)

ddtrace.patch(logging=True)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
          'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

@app.route('/internal-metrics', methods=['GET'])
def internal_metrics():
    # Fetch metrics from the backend service
    backend_url = 'http://datadog-app-backend-service:5000/metrics'  # Internal service URL
    try:
        response = requests.get(backend_url)
        response.raise_for_status()  # Raise an error for bad responses
        return jsonify(response.json())
    except Exception as e:
        log.error("Failed to fetch metrics from backend: %s", e)
        return jsonify(error="Failed to fetch metrics"), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    log.info("Serving metrics")

    # Load Kubernetes config
    config.load_incluster_config()

    # Create an API client
    v1 = client.CoreV1Api()

    # Get the node name from the environment
    node_name = os.getenv('NODE_NAME')

    # Get node metrics
    try:
        node_metrics = v1.read_node(name=node_name)
        cpu_usage = node_metrics.status.allocatable['cpu']
        memory_usage = node_metrics.status.allocatable['memory']

        # Log metrics
        log.info("CPU Usage: %s", cpu_usage)
        log.info("Memory Usage: %s", memory_usage)

    except Exception as e:
        log.error("Failed to fetch metrics: %s", e)
        return jsonify(error="Failed to fetch metrics"), 500

    # Return metrics
    return jsonify(cpu=cpu_usage, memory=memory_usage)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)