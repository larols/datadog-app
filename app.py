import logging
from ddtrace import tracer, patch
from ddtrace.profiling import Profiler
from flask import Flask, render_template_string, request
import random
import time

# Configure logging
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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
    log.info("Rendering index page.")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    log.info("Button click received.")
    with tracer.trace("button_click.root") as root_span:
        root_span.set_tag("button", "clicked")

        # Log the creation of the root span
        log.info("Created root span with ID: %s", root_span.span_id)

        # Simulate some processing with a child span
        time.sleep(random.uniform(0.1, 0.5))
        with tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            
            # Log the creation of the child span
            log.info("Created child span with ID: %s", child_span.span_id)

            time.sleep(random.uniform(0.1, 0.5))

    log.info("Button click processed successfully.")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

