import logging
from flask import Flask, render_template_string, request
import random
import time
from ddtrace import tracer, patch_all
from ddtrace.contrib.logging import patch as logging_patch
from ddtrace.profiling import Profiler

# 1. Patch all integrations including logging
patch_all(logging=True)

# 2. Start Datadog Profiler early
prof = Profiler(
    env="production",
    service="datadog-app",
    version="1.0",
)
prof.start()

# 3. Configure logging format
LOG_FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
    '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
    'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s'
)

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for verbose output
    format=LOG_FORMAT,
)

log = logging.getLogger(__name__)

# 4. Set Datadog service, env, and version globally
from ddtrace import config
config.service = "datadog-app"
config.env = "production"
config.version = "1.0"

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
    log.debug("Rendering index page.")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    log.debug("Button click received.")

    with tracer.trace("button_click.root") as root_span:
        root_span.set_tag("button", "clicked")
        log.debug("Started root span for button click.")

        # Simulate some processing with a child span
        with tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            log.debug("Started child span for processing task.")

            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            log.debug(f"Processing task for {processing_time:.2f} seconds.")
            time.sleep(processing_time)

        log.debug("Child span processing complete.")

    log.debug("Button click processing complete.")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    log.debug("Starting the Flask application.")
    app.run(host='0.0.0.0', port=5000)

