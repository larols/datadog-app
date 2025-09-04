# app_chat.py
import os
import time
import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI

# --- Datadog APM + log correlation ---
from ddtrace import patch_all, config, tracer

# Auto-instrument everything we can, and enable logging correlation
patch_all(logging=True)
config.flask["service_name"] = os.getenv("DD_SERVICE", "datadog-app-chat")

# Log format w/ Datadog trace correlation fields
FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s] '
    '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
    'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
    '- %(message)s'
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger("chat")
log.setLevel(logging.INFO)

# Optional: DogStatsD metrics (safe if agent present; no-op otherwise)
try:
    from datadog import statsd
except Exception:  # pragma: no cover
    class _NoopStatsd:
        def increment(self, *a, **k): pass
        def timing(self, *a, **k): pass
        def gauge(self, *a, **k): pass
    statsd = _NoopStatsd()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# NEVER put your key in the frontend
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"ok": True}), 200

# ---- Non-streaming (simple JSON) ----
@app.route("/api/chat", methods=["POST"])
def chat_once():
    t0 = time.time()
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages") or []
    system = payload.get("system") or "You are a helpful assistant."
    model = payload.get("model") or "gpt-4o"

    # Keep PII/secrets out of logs; log only sizes and metadata
    prompt_chars = sum(len(m.get("content", "")) for m in messages)

    try:
        resp = client.responses.create(
            model=model,
            instructions=system,
            input=messages_to_responses_input(messages),
        )
        text = resp.output_text or ""
        dt_ms = int((time.time() - t0) * 1000)

        # Metrics + logs
        statsd.increment("chat.request.count", tags=[f"model:{model}", "stream:false"])
        statsd.timing("chat.request.latency_ms", dt_ms, tags=[f"model:{model}", "stream:false"])
        statsd.gauge("chat.output.length_chars", len(text), tags=[f"model:{model}"])
        statsd.gauge("chat.prompt.length_chars", prompt_chars, tags=[f"model:{model}"])

        log.info(
            "chat_once completed",
            extra={
                "model": model,
                "response_id": getattr(resp, "id", None),
                "latency_ms": dt_ms,
                "prompt_chars": prompt_chars,
                "output_chars": len(text),
            },
        )
        return jsonify({"text": text, "response_id": resp.id}), 200

    except Exception as e:
        dt_ms = int((time.time() - t0) * 1000)
        statsd.increment("chat.request.errors", tags=[f"model:{model}", "stream:false"])
        log.exception("chat_once failed", extra={"model": model, "latency_ms": dt_ms})
        return jsonify({"error": "chat failed"}), 500

# ---- Streaming via SSE ----
@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    t0 = time.time()
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages") or []
    system = payload.get("system") or "You are a helpful assistant."
    model = payload.get("model") or "gpt-4o"

    prompt_chars = sum(len(m.get("content", "")) for m in messages)

    def sse():
        output_len = 0
        try:
            stream = client.responses.stream(
                model=model,
                instructions=system,
                input=messages_to_responses_input(messages),
            )
            with stream as events:
                for event in events:
                    if hasattr(event, "delta") and isinstance(event.delta, str) and event.delta:
                        output_len += len(event.delta)
                        yield f"data: {event.delta}\n\n"
                # signal completion
                yield "event: done\ndata: [DONE]\n\n"
        except Exception:
            # Bubble an error to the client stream
            log.exception("chat_stream failed during SSE")
            yield "event: error\ndata: stream_error\n\n"
        finally:
            dt_ms = int((time.time() - t0) * 1000)
            statsd.increment("chat.request.count", tags=[f"model:{model}", "stream:true"])
            statsd.timing("chat.request.latency_ms", dt_ms, tags=[f"model:{model}", "stream:true"])
            statsd.gauge("chat.output.length_chars", output_len, tags=[f"model:{model}"])
            statsd.gauge("chat.prompt.length_chars", prompt_chars, tags=[f"model:{model}"])
            log.info(
                "chat_stream completed",
                extra={
                    "model": model,
                    "latency_ms": dt_ms,
                    "prompt_chars": prompt_chars,
                    "output_chars": output_len,
                },
            )

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return Response(sse(), headers=headers)

def messages_to_responses_input(messages):
    # Keep it simple; redact prompts from logs but format prompt for the model
    stitched = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "
