from flask import Flask, render_template_string, request
import time
import random
import logging
import ddtrace

ddtrace.patch(logging=True)

app = Flask(__name__)

# Configure Datadog logging
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# HTML template with a button
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App</title>
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
<script
    src="https://www.datadoghq-browser-agent.com/eu1/v5/datadog-rum.js"
    type="text/javascript">
</script>
<script>
    window.DD_RUM && window.DD_RUM.init({
      clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',
      applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',
      // `site` refers to the Datadog site parameter of your organization
      // see https://docs.datadoghq.com/getting_started/site/
      site: 'datadoghq.eu',
      service: 'datadog-app',
      allowedTracingUrls: [
                (url) => url.startsWith("http://")
            ],
      env: 'production',
      // Specify a version number to identify the deployed version of your application in Datadog
      version: '1.3.6',
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
@ddtrace.tracer.wrap()
def index():
    log.info("Rendering index page")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
@ddtrace.tracer.wrap()
def click():
    log.info("Button clicked, processing...")
    try:
        # Simulate some processing
        time.sleep(random.uniform(0.1, 0.5))
        log.info("Processing done")
        return "Button clicked! Processing done."
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)
        return "An error occurred during processing", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
