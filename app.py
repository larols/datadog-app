# Test
from flask import Flask
import time
import random
import threading
from ddtrace import tracer, patch

# Patch Flask to enable tracing
patch(flask=True)

app = Flask(__name__)

@app.route('/')
def index():
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)  # Simulate some processing
    return f"Hello! Processing time: {processing_time:.2f}s\n"

@app.route('/data')
def data():
    processing_time = random.uniform(0.2, 1.0)
    time.sleep(processing_time)  # Simulate data processing
    return f"Data processed in {processing_time:.2f}s\n"

def periodic_task():
    while True:
        with tracer.trace("background.periodic_task") as span:
            span.set_tag("task", "periodic_task")
            processing_time = random.uniform(0.5, 1.5)
            time.sleep(processing_time)  # Simulate some background work
            print(f"Background task completed in {processing_time:.2f}s")
        time.sleep(30)  # Wait for 30 seconds before running again

if __name__ == '__main__':
    # Start the background thread
    threading.Thread(target=periodic_task, daemon=True).start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)

