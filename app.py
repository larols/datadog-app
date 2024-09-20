from flask import Flask, render_template_string, request
import time
import random
import logging
import ddtrace

# Enable Datadog tracing for the logging module
ddtrace.patch(logging=True)

app = Flask(__name__)

# Enable Flask debug mode
app.config['DEBUG'] = True

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
            flex-direction: column;
        }
        button {
            font-size: 20px;
            padding: 10px 20px;
        }
        nav a {
            margin: 5px;
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

        // Random user data generation for 3 customer segments
        (function() {
          const firstNames = ["John", "Jane", "Sam", "Chris", "Pat", "Alex", "Jamie", "Taylor", "Jordan", "Casey"];
          const lastNames = ["Smith", "Doe", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Clark", "Lee"];
          const customerSegments = [
            { idPrefix: 'cust-a-', domain: 'example.com' },
            { idPrefix: 'cust-b-', domain: 'example.io' },
            { idPrefix: 'cust-c-', domain: 'example.net' }
          ];

          function getRandomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
          }

          function generateUser() {
            const firstName = firstNames[getRandomInt(0, firstNames.length - 1)];
            const lastName = lastNames[getRandomInt(0, lastNames.length - 1)];
            const segment = customerSegments[getRandomInt(0, customerSegments.length - 1)];

            const id = `${segment.idPrefix}${getRandomInt(1000, 9999)}`;
            const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${segment.domain}`;

            return { id, name: `${firstName} ${lastName}`, email };
          }

          const randomUser = generateUser();
          window.DD_RUM?.setUser({
            id: randomUser.id,
            name: randomUser.name,
            email: randomUser.email
          });

          // Send user data to the server when visiting the profile page
          document.addEventListener('DOMContentLoaded', function() {
            if (window.location.pathname === '/profile') {
              fetch('/profile', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(randomUser)
              }).then(response => response.text())
                .then(data => document.body.innerHTML = data)
                .catch(error => console.error('Error:', error));
            }
          });

        })();
    </script>
</head>
<body>
    <nav>
        <a href="/">Home</a> | 
        <a href="/about">About</a> | 
        <a href="/metrics">Metrics</a> | 
        <a href="/error">Simulate Error</a> | 
        <a href="/profile">User Profile</a>
    </nav>
    <hr>
    {% block content %}{% endblock %}
</body>
</html>
'''

@app.route('/')
def index():
    log.info("Rendering index page")
    return render_template_string('''
    {% extends "layout.html" %}
    {% block content %}
    <h2>Main Page</h2>
    <p>This is the main page. Use the navigation to explore other views.</p>
    <form method="POST" action="/click">
        <input type="text" name="user_input" placeholder="Enter something"/>
        <button type="submit">Click me!</button>
    </form>
    {% endblock %}
    ''', layout=html_template)

@app.route('/about')
def about():
    log.info("Rendering about page")
    return render_template_string('''
    {% extends "layout.html" %}
    {% block content %}
    <h2>About Page</h2>
    <p>This is a simple app demonstrating Flask with Datadog integration.</p>
    {% endblock %}
    ''', layout=html_template)

@app.route('/metrics')
def metrics():
    log.info("Rendering metrics page")
    cpu = random.uniform(0, 100)
    memory = random.uniform(0, 16)
    return render_template_string('''
    {% extends "layout.html" %}
    {% block content %}
    <h2>Metrics</h2>
    <p>CPU Utilization: {{ cpu }}%</p>
    <p>Memory Utilization: {{ memory }} GB</p>
    {% endblock %}
    ''', cpu=cpu, memory=memory, layout=html_template)

@app.route('/error')
def error():
    log.info("Simulating an error")
    raise Exception("This is a simulated error for testing purposes")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        log.info("Rendering user profile page")
        user_data = request.json
        return render_template_string('''
        {% extends "layout.html" %}
        {% block content %}
        <h2>User Profile</h2>
        <p><strong>ID:</strong> {{ user.id }}</p>
        <p><strong>Name:</strong> {{ user.name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        {% endblock %}
        ''', user=user_data, layout=html_template)
    return render_template_string('''
    {% extends "layout.html" %}
    {% block content %}
    <h2>User Profile</h2>
    <p>Loading user profile...</p>
    {% endblock %}
    ''', layout=html_template)

@app.route('/click', methods=['POST'])
def click():
    user_input = request.form.get('user_input', '')
    log.info("Button clicked, processing input: %s", user_input)
    try:
        processing_time = random.uniform(0.1, 0.9)
        log.debug("Simulating processing time of %.2f seconds", processing_time)
        time.sleep(processing_time)
        log.info("Processing complete. User input: %s", user_input)
        return f"Button clicked! You entered: {user_input}"
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)
        return "An error occurred during processing", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)