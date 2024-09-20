import os
import logging
import random
import time
from flask import Flask, jsonify, request, render_template_string
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

@app.route('/')
def index():
    log.info("Rendering index page")
    return render_template_string('''
    <h2>Main Page</h2>
    <p>This is the main page. Use the navigation to explore other views.</p>
    <form method="POST" action="/click">
        <input type="text" name="user_input" placeholder="Enter something" required />
        <button type="submit">Click me!</button>
    </form>
    ''')

@app.route('/click', methods=['POST'])
def click():
    user_input = request.form.get('user_input', '')
    log.info("Button clicked, processing input: %s", user_input)  # Log user input
    try:
        processing_time = random.uniform(0.1, 0.9)
        log.debug("Simulating processing time of %.2f seconds", processing_time)
        time.sleep(processing_time)
        log.info("Processing complete. User input: %s", user_input)

        # Log the user input for further tracking
        log.info("User input logged: %s", user_input)  # Additional log entry for user input

        return f"Button clicked! You entered: {user_input}"
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)
        return "An error occurred during processing", 500

@app.route('/internal-metrics', methods=['GET'])
def internal_metrics():
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
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    node_name = os.getenv('NODE_NAME')

    try:
        node_metrics = v1.read_node(name=node_name)
        cpu_usage = node_metrics.status.allocatable['cpu']
        memory_usage = node_metrics.status.allocatable['memory']
        log.info("CPU Usage: %s", cpu_usage)
        log.info("Memory Usage: %s", memory_usage)
    except Exception as e:
        log.error("Failed to fetch metrics: %s", e)
        return jsonify(error="Failed to fetch metrics"), 500

    return jsonify(cpu=cpu_usage, memory=memory_usage)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)