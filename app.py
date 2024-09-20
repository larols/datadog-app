from flask import Flask, render_template_string, request
import time
import random
import logging
import ddtrace

# ddtrace.patch(logging=True) # Enable Datadog tracing for the logging module
ddtrace.patch_all() # Enable tracing for all available libraries

app = Flask(__name__)

# Enable Flask debug mode
app.config['DEBUG'] = False

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# HTML template with modern styles
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        /* Add a modern font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        /* Global styles */
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            flex-direction: column;
        }

        /* Navigation bar */
        nav {
            margin-bottom: 20px;
        }

        nav a {
            text-decoration: none;
            color: #3498db;
            font-size: 18px;
            margin: 0 10px;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        nav a:hover {
            color: #2c3e50;
        }

        /* Page container */
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }

        /* Buttons */
        button {
            font-size: 18px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #2980b9;
        }

        /* Input fields */
        input[type="text"] {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            margin-right: 10px;
            width: 60%;
        }

        input[type="text"]:focus {
            border-color: #3498db;
            outline: none;
        }

        hr {
            width: 80%;
            margin: 20px auto;
            border: none;
            height: 1px;
            background-color: #ddd;
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
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

# Define Flask routes
@app.route('/')
def index():
    log.info("Rendering index page")
    return render_template_string(html_template.replace('{% block content %}{% endblock %}', '''
    <h2>Main Page</h2>
    <p>This is the main page. Use the navigation to explore other views.</p>
    <form method="POST" action="/click">
        <input type="text" name="user_input" placeholder="Enter something"/>
        <button type="submit">Click me!</button>
    </form>
    '''), title="Main Page")

@app.route('/about')
def about():
    log.info("Rendering about page")
    return render_template_string(html_template.replace('{% block content %}{% endblock %}', '''
    <h2>About Page</h2>
    <p>This is a simple app demonstrating Flask with Datadog integration.</p>
    '''), title="About Page")

@app.route('/metrics')
def metrics():
    log.info("Rendering metrics page")
    cpu = round(random.uniform(0, 100), 1)
    memory = round(random.uniform(0, 16), 1)
    return render_template_string(html_template.replace('{% block content %}{% endblock %}', '''
    <h2>Metrics</h2>
    <p>CPU Utilization: {{ cpu }}%</p>
    <p>Memory Utilization: {{ memory }} GB</p>
    '''), cpu=cpu, memory=memory, title="Metrics")

@app.route('/error')
def error():
    log.info("Simulating an error")

    # Simulate a backend error and propagate it to the client
    try:
        raise Exception("This is a simulated server-side error for testing purposes")
    except Exception as e:
        log.error("Error occurred: %s", str(e), exc_info=True)

        # Return an HTML page that will cause a client-side JavaScript error
        error_page = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Simulated Client-Side Error</title>
            <script>
                // This will trigger a client-side JavaScript error visible in Datadog RUM
                throw new Error("Simulated JavaScript error triggered for testing purposes");
            </script>
        </head>
        <body>
            <h1>Simulated Client-Side Error</h1>
            <p>This is a page that intentionally triggers a JavaScript error.</p>
        </body>
        </html>
        '''
        
        # Return the HTML page with a 500 status code
        return error_page, 500

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        log.info("Rendering user profile page")
        user_data = request.json
        return render_template_string(html_template.replace('{% block content %}{% endblock %}', '''
        <h2>User Profile</h2>
        <p><strong>ID:</strong> {{ user.id }}</p>
        <p><strong>Name:</strong> {{ user.name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        '''), user=user_data, title="User Profile")
    return render_template_string(html_template.replace('{% block content %}{% endblock %}', '''
    <h2>User Profile</h2>
    <p>Loading user profile...</p>
    '''), title="User Profile")

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