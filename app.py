import logging
from flask import Flask, render_template_string, request
import random
import time
import ddtrace  # Import ddtrace, which includes everything you need

# Enable runtime metrics and dynamic instrumentation
ddtrace.runtime.RuntimeMetrics.enable()
ddtrace.debugging.DynamicInstrumentation.enable()

# Start the profiler
prof = ddtrace.profiling.Profiler(
    env="production",
    service="datadog-app",
)
prof.start()

# Patch Flask to enable tracing
ddtrace.patch(flask=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable automatic correlation between logs and traces
ddtrace.config.logs_injection = True

app = Flask(__name__)

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
    logger.info("Rendering index page")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    logger.info("Button clicked. Starting processing...")
    
    with ddtrace.tracer.trace("button_click.root") as root_span:
        root_span.set_tag("button", "clicked")
        
        # Simulate some processing with a child span
        time_to_sleep = random.uniform(0.1, 0.5)
        logger.info(f"Root span processing. Sleeping for {time_to_sleep:.2f} seconds.")
        time.sleep(time_to_sleep)
        
        with ddtrace.tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            time_to_sleep_child = random.uniform(0.1, 0.5)
            logger.info(f"Child span processing. Sleeping for {time_to_sleep_child:.2f} seconds.")
            time.sleep(time_to_sleep_child)
        
    logger.info("Processing done. Returning response.")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000)
