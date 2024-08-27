from flask import Flask, render_template_string, request
import random
import time
import ddtrace
import logging
from ddtrace import tracer, patch
from ddtrace.profiling import Profiler
from ddtrace.runtime import RuntimeMetrics
from ddtrace.debugging import DynamicInstrumentation

# Enable runtime metrics and dynamic instrumentation
RuntimeMetrics.enable()
DynamicInstrumentation.enable()

# Start profiling
prof = Profiler(
    env="production",
    service="datadog-app",
    version="1.0",
)
prof.start()

# Patch Flask to enable tracing
patch(flask=True)

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom formatter to include trace_id and span_id
class DatadogLogFormatter(logging.Formatter):
    def format(self, record):
        # Get the current trace and span IDs
        trace_id = tracer.current_trace_context().trace_id if tracer.current_trace_context() else 'None'
        span_id = tracer.current_trace_context().span_id if tracer.current_trace_context() else 'None'
        
        # Add trace_id and span_id to the log record
        record.trace_id = trace_id
        record.span_id = span_id
        
        # Format the message
        return super(DatadogLogFormatter, self).format(record)

# Apply the custom formatter
formatter = DatadogLogFormatter('[%(levelname)s] trace_id=%(trace_id)s span_id=%(span_id)s: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# HTML template with a button and Datadog RUM script
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
    <script src="https://www.datadoghq-browser-agent.com/eu1/v5/datadog-rum.js" type="text/javascript"></script>
    <script>
    window.DD_RUM && window.DD_RUM.init({
        clientToken: 'pubed1d766fe7d2e291e79fedaba88e7c5a',
        applicationId: 'd876d594-0575-451c-adff-ee5c5aa86b1d',
        site: 'datadoghq.eu',
        service: 'datadog-app',
        env: 'production',
        sessionSampleRate: 100,
        sessionReplaySampleRate: 100,
        trackUserInteractions: true,
        trackResources: true,
        trackLongTasks: true,
        defaultPrivacyLevel: 'allow',
        allowedTracingUrls: [
            // Match the base URL and any path
            /^http:\/\/192\.168\.50\.242\/.*$/
        ],
        });
    </script>
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
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    with tracer.trace("button_click.root") as root_span:
        root_span.set_tag("button", "clicked")
        
        # Log the button click with trace and span ID
        logger.info("Button was clicked.")

        # Simulate some processing with a child span
        time.sleep(random.uniform(0.1, 0.5))
        with tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            time.sleep(random.uniform(0.1, 0.5))

            # Log the processing with trace and span ID
            logger.info("Child task processing completed.")
        
    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
