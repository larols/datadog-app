from flask import Flask, render_template_string, request
import time
import random
import logging
import ddtrace
import psycopg2
from psycopg2 import sql

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

# Database connection settings
DB_HOST = "datadog-app-db"  # Hostname of the PostgreSQL container
DB_PORT = "5432"
DB_NAME = "mydb"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"

# Connect to PostgreSQL
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        log.info("Database connection established")
        return connection
    except Exception as e:
        log.error("Failed to connect to the database", exc_info=True)
        raise

# Initialize the database (run this once, or include in an init script)
def init_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_inputs (
                id SERIAL PRIMARY KEY,
                user_input TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()
        log.info("Database initialized")
    except Exception as e:
        log.error("Failed to initialize the database", exc_info=True)
        raise

# Call init_db() to initialize the database table
init_db()

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
    // Function to fetch the version from version.json
    async function fetchVersion() {
        try {
            const response = await fetch('/version.json');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            return data.version;
        } catch (error) {
            console.error('Error fetching version:', error);
            return 'unknown'; // Fallback version in case of an error
        }
    }

    // Initialize Datadog RUM with the fetched version
    (async () => {
        const version = await fetchVersion();
        window.DD_RUM && window.DD_RUM.init({
            clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',
            applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',
            site: 'datadoghq.eu',
            service: 'datadog-app',
            allowedTracingUrls: [
                (url) => url.startsWith("http://")
            ],
            env: 'production',
            version: version,
            sessionSampleRate: 100,
            sessionReplaySampleRate: 100,
            trackUserInteractions: true,
            trackResources: true,
            trackLongTasks: true,
            defaultPrivacyLevel: 'allow',
        });
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
        processing_time = random.uniform(0.1, 0.5)
        log.debug("Simulating processing time of %.2f seconds", processing_time)
        time.sleep(processing_time)

        # Store the user input in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO user_inputs (user_input) VALUES (%s)",
            (user_input,)
        )
        connection.commit()

        # Fetch the latest user input
        cursor.execute("SELECT user_input FROM user_inputs ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        log.info("Processing complete. Latest user input: %s", result[0])
        # Return a response that includes user input without escaping
        return f"Button clicked! You entered: {result[0]}"
    except Exception as e:
        log.error("An error occurred during processing", exc_info=True)
        return "An error occurred during processing", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
