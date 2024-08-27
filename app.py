import logging
from flask import Flask, render_template_string, request
import random
import time
from ddtrace import tracer, patch
from ddtrace.profiling import Profiler
from ddtrace.context import Context

# Configure logging with Datadog context
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)  # Raise the logging level to DEBUG for more logs

# Start Datadog Profiler
prof = Profiler(
    env="production",
    service="datadog-app",
    version="1.0",
)
prof.start()

# Patch Flask to enable tracing
patch(flask=True)

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
        context = root_span.context
        log.debug(f"Created root span with ID: {root_span.span_id}, Trace ID: {context.trace_id}")
        
        # Simulate some processing with a child span
        time.sleep(random.uniform(0.1, 0.5))
        log.debug("Starting child span processing.")
        
        with tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            log.debug(f"Created child span with ID: {child_span.span_id}, Trace ID: {child_span.context.trace_id}")

            # Simulate more processing
            time.sleep(random.uniform(0.1, 0.5))

    log.debug("Button click processing complete.")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    log.debug("Starting the Flask application.")
    app.run(host='0.0.0.0', port=5000)

