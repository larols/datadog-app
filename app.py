from flask import Flask, render_template_string, request
import random
import time
from ddtrace import tracer, patch
from ddtrace.profiling import Profiler

prof = Profiler(
    env="production",  # if not specified, falls back to environment variable DD_ENV
    service="datadog-app",  # if not specified, falls back to environment variable DD_SERVICE
    version="1.0",   # if not specified, falls back to environment variable DD_VERSION
)
prof.start()  # Should be as early as possible, eg before other imports, to ensure everything is profiled

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
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    with tracer.trace("button_click.root") as root_span:
        root_span.set_tag("button", "clicked")

        # Simulate some processing with a child span
        time.sleep(random.uniform(0.1, 0.5))
        with tracer.trace("button_click.child") as child_span:
            child_span.set_tag("child_task", "processing")
            time.sleep(random.uniform(0.1, 0.5))

    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)