# SIMULATING NEW VERSION

from flask import Flask, render_template_string, request
import time
import random
import logging
import ddtrace

# Enable Datadog tracing for the logging module
ddtrace.patch(logging=True)

app = Flask(__name__)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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
    window.DD_RUM && window.DD_RUM.init({
      clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',
      applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',
      site: 'datadoghq.eu',
      service: 'datadog-app',
      allowedTracingUrls: [
                (url) => url.startsWith("http://")
            ],
      env: 'production',
      version: 'VERSION',
      
      sessionSampleRate: 100,
      sessionReplaySampleRate: 100,
      trackUserInteractions: true,
      trackResources: true,
      trackLongTasks: true,
      defaultPrivacyLevel: 'allow',
    });

    // Random user data generation
    (function() {
      // Arrays for random name generation
      const firstNames = ["John", "Jane", "Sam", "Chris", "Pat", "Alex", "Jamie", "Taylor", "Jordan", "Casey"];
      const lastNames = ["Smith", "Doe", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Clark", "Lee"];

      // Generate a random integer between min and max (inclusive)
      function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
      }

      // Generate a random user
      function generateUser() {
        const id = getRandomInt(1100, 1200); // ID range 1100-1200
        const firstName = firstNames[getRandomInt(0, firstNames.length - 1)];
        const lastName = lastNames[getRandomInt(0, lastNames.length - 1)];
        const name = `${firstName} ${lastName}`;
        const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`;

        return { id, name, email };
      }

      // Generate and send a single randomized user to DD_RUM
      const user = generateUser();
      window.DD_RUM && window.DD_RUM.setUser({
        id: user.id,
        name: user.name,
        email: user.email
      });
      console.log(`User sent: ${user.id}, ${user.name}, ${user.email}`);
    })();
</script>    

</head>
<!-- User input for testing code vulnerable to xss  -->
<body>
    <form method="POST" action="/click">
        <input type="text" name="user_input" placeholder="Enter something"/>
        <button type="submit">Click me!</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    log.info("Rendering index page")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    user_input = request.form.get('user_input', '')
    log.info("Button clicked, processing input: %s", user_input)
    try:
        # Simulate some processing time with a random delay
        processing_time = random.uniform(0.1, 0.9)
        log.debug("Simulating processing time of %.2f seconds", processing_time)
        time.sleep(processing_time)

        log.info("Processing complete. User input: %s", user_input)
        # Return a response that includes user input without escaping
        return f"Button clicked! You entered: {user_input}"
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)
        return "An error occurred during processing", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
