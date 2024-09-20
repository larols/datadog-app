from flask import Flask, jsonify, request
import random, logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@app.route('/metrics', methods=['GET'])
def metrics():
    log.info("Serving metrics")
    cpu = round(random.uniform(0, 100), 1)
    memory = round(random.uniform(0, 16), 1)
    return jsonify(cpu=cpu, memory=memory)

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