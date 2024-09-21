from flask import Flask, jsonify
from ddtrace import patch_all
import logging

# Patch all supported libraries for Datadog tracing
patch_all()

# Initialize the Flask app
app = Flask(__name__)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
          'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s')

# Configure logging
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Initialize a visit counter
visit_count = 0

@app.route('/api/views', methods=['GET'])
def get_views_data():
    global visit_count
    visit_count += 1  # Increment the visit counter

    # Log the visit count
    log.info(f"Visitor count: {visit_count}")

    data = {
        "id": 1,
        "text": f"Views: You are visitor number {visit_count}!"
    }
    return jsonify(data)

@app.route('/api/visits', methods=['GET'])
def get_visit_count():
    log.info("Fetching visit count")
    return jsonify({"visit_count": visit_count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Expose the app on port 5000