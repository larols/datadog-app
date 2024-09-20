from flask import Flask, jsonify, request, CORS
from kubernetes import client, config
import os
import logging
import random
from ddtrace import patch_all

# Patch all supported libraries
patch_all()

app = Flask(__name__)
CORS(app)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

@app.route('/metrics', methods=['GET'])
def metrics():
    log.info("Serving metrics")

    # Load Kubernetes config
    config.load_incluster_config()  # Use this if running inside a cluster

    # Create an API client
    v1 = client.CoreV1Api()

    # Get the node name from the environment
    node_name = os.getenv('NODE_NAME')  # Make sure this is set in your deployment manifest

    # Get node metrics
    try:
        node_metrics = v1.read_node(name=node_name)
        cpu_usage = node_metrics.status.allocatable['cpu']  # Total allocatable CPU
        memory_usage = node_metrics.status.allocatable['memory']  # Total allocatable memory

        # Log CPU and memory metrics
        log.info("CPU Usage: %s", cpu_usage)
        log.info("Memory Usage: %s", memory_usage)
    except Exception as e:
        log.error("Failed to fetch metrics: %s", e)
        return jsonify(error="Failed to fetch metrics"), 500

    # Return metrics
    return jsonify(cpu=cpu_usage, memory=memory_usage)

@app.route('/error', methods=['GET'])
def error():
    log.info("Simulating error")
    raise Exception("Simulated error for testing")

@app.route('/profile', methods=['POST'])
def profile():
    user_data = request.json
    log.info(f"Received profile data: {user_data}")
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)