from flask import Flask, jsonify
import logging
import random
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor  

# OpenTelemetry Resource Configuration
resource = Resource(attributes={
    "service.name": 'datadog-app-quotes',
    "service.version": '1.0.0',
    "service.environment": 'production'
})

# Initialize OTel Tracer and Span Processor
provider = TracerProvider(resource=resource)
otlp_endpoint = 'http://otel-agent.otel.svc.cluster.local:4318'
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Initialize Flask app 
app = Flask(__name__)

# Enable Flask and Logging Instrumentation for OTel
FlaskInstrumentor().instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True)

# Set Up Logging Format 
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[otel.trace_id=%(otelTraceId)s otel.span_id=%(otelSpanId)s] - %(message)s')
logging.basicConfig(format=FORMAT, level=logging.INFO)
log = logging.getLogger(__name__)

# Predefined list of quotes
QUOTES = [
    {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
    {"quote": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
    {"quote": "Don’t be afraid to give up the good to go for the great.", "author": "John D. Rockefeller"},
    {"quote": "Opportunities don't happen. You create them.", "author": "Chris Grosser"},
    {"quote": "Don’t wait. The time will never be just right.", "author": "Napoleon Hill"},
    {"quote": "Success is not in what you have, but who you are.", "author": "Bo Bennett"},
    {"quote": "Do not be embarrassed by your failures, learn from them and start again.", "author": "Richard Branson"},
    {"quote": "Success is how high you bounce when you hit bottom.", "author": "General George Patton"},
    {"quote": "Don’t be pushed around by the fears in your mind. Be led by the dreams in your heart.", "author": "Roy T. Bennett"},
    {"quote": "Everything you’ve ever wanted is on the other side of fear.", "author": "George Addair"}
]

@app.route('/api/quotes/random', methods=['GET'])
def fetch_random_quote():
    """Fetch a random motivational quote."""
    try:
        with trace.get_tracer(__name__).start_as_current_span("fetch-random-quote"):
            random_quote = random.choice(QUOTES)
            log.info(f"Random quote fetched: {random_quote['quote']} by {random_quote['author']}")
            return jsonify(random_quote), 200
    except Exception as e:
        log.error(f"Error fetching random quote: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
