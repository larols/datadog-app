from flask import Flask, render_template_string
from ddtrace import tracer, patch
from ddtrace.debugging import DynamicInstrumentation
from ddtrace.profiling import Profiler

import time
import random
import logging
from pythonjsonlogger import jsonlogger

# Enable dynamic instrumentation
DynamicInstrumentation.enable()

# Configure and start the Profiler
prof = Profiler(
    env="production",  # Environment (can be set to a different value as needed)
    service="datadog-app",  # Service name (can be set to a different value as needed)
    version="1.0",  # Version of the application (can be set to a different value as needed)
)
prof.start()  # Start profiling

# Patch Flask to enable tracing
patch(flask=True)

app = Flask(__name__)

# Configure JSON logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the desired log level

# Create a handler for output (console, file, etc.)
handler = logging.StreamHandler()

# Create a JSON formatter
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# HTML template with a button
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Datadog App</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        button {
            font-size: 20px;
            padding: 10px 20px;
        }
    </style>
</head>
<body>
    <form method="POST" action="/click">
        <button type="submit">Click me!</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    app.logger.info("Rendering index page")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    app.logger.info("Button clicked, processing...")
    # Simulate some processing
    time.sleep(random.uniform(0.1, 0.5))
    app.logger.info("Processing done")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
