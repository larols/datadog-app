from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template with a button and Datadog RUM script
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Flask App</title>
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
    <!-- Include Datadog RUM JavaScript library -->
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
        allowedTracingUrls: [
            // Match the base URL and any path
            /^http:\/\/192\.168\.50\.242\/.*$/
        ],
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
    # Render the HTML template for the home page
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    # Simulate processing
    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
