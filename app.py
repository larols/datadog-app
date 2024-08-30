# Import necessary modules
from flask import Flask, render_template_string, request  # Flask web framework and utilities
import time  # For simulating processing delay
import random  # For generating random delays
import logging  # For logging information
import ddtrace  # For Datadog tracing and monitoring

# Enable Datadog tracing for the logging module
ddtrace.patch(logging=True)

# Create a new Flask web application instance
app = Flask(__name__)

# Configure the format for logging messages, including Datadog-specific fields
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

# Set up logging with the specified format
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)  # Get a logger instance for this module
log.setLevel(logging.INFO)  # Set logging level to INFO

# HTML template that will be rendered and sent to the client
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
    <!-- Include Datadog RUM (Real User Monitoring) -->
    <script
        src="https://www.datadoghq-browser-agent.com/eu1/v5/datadog-rum.js"
        type="text/javascript">
    </script>
    <script>
        // Initialize Datadog RUM with your configuration
        window.DD_RUM && window.DD_RUM.init({
          clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',  // Your Datadog RUM client token
          applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',  // Your Datadog RUM application ID
          site: 'datadoghq.eu',  // Datadog site, based on your organization
          service: 'datadog-app',  // Service name reported to Datadog
          allowedTracingUrls: [
                    (url) => url.startsWith("http://")  // Allow tracing for HTTP requests
                ],
          env: 'production',  // Environment name (e.g., production)
          version: '1.3.6',  // Version of the application
          sessionSampleRate: 100,  // Percentage of sessions to sample for RUM
          sessionReplaySampleRate: 100,  // Percentage of sessions to capture replay data
          trackUserInteractions: true,  // Track user interactions like clicks
          trackResources: true,  // Track network requests and assets
          trackLongTasks: true,  // Track long tasks that block the main thread
          defaultPrivacyLevel: 'allow',  // Privacy level configuration
        });
    </script>
</head>
<body>
    <!-- Simple form with a button to trigger a POST request -->
    <form method="POST" action="/click">
        <button type="submit">Click me!</button>
    </form>
</body>
</html>
'''

# Route for the root URL
@app.route('/')
@ddtrace.tracer.wrap()  # Wrap this function with Datadog tracing
def index():
    log.info("Rendering index page")  # Log that the index page is being rendered
    return render_template_string(html_template)  # Render the HTML template

# Route to handle the button click
@app.route('/click', methods=['POST'])
@ddtrace.tracer.wrap()  # Wrap this function with Datadog tracing
def click():
    log.info("Button clicked, processing...")  # Log that the button was clicked
    try:
        # Simulate some processing time with a random delay
        time.sleep(random.uniform(0.1, 0.5))
        log.info("Processing done")  # Log that processing is complete
        return "Button clicked! Processing done."  # Return a success message
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)  # Log the error with exception details
        return "An error occurred during processing", 500  # Return an error message and status code 500

# Entry point for running the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the app on all available IPs on port 5000
