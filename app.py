from flask import Flask
import time
import random

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

