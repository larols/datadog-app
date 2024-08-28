from flask import Flask, render_template_string
import time
import random
import logging

app = Flask(__name__)

# Configure default logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the desired log level

# Create a handler for output (console, file, etc.)
handler = logging.StreamHandler()

# Create a default formatter
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

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
    app.logger.info("Rendering index page")
    return render_template_string(html_template)

@app.route('/click', methods=['POST'])
def click():
    app.logger.info("Button clicked, processing...")
    # Simulate some processing
    time.sleep(random.uniform(0.1, 0.5))
    app.logger.info("Processing done")
    return "Button clicked! Processing done."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
