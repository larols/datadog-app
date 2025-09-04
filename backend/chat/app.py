# app_chat.py
import os
import time
import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI

# --- Datadog APM + log correlation + LLM Obs (OpenAI ONLY) ---
from ddtrace import patch, config, tracer
from ddtrace.llmobs import LLMObs

# Enable LLM Observability, but do NOT auto-enable every LLM integration
LLMObs.enable(integrations_enabled=False)

# Instrument ONLY what we need (avoid patch_all):
# - flask/requests/logging for web traces + log correlation
# - openai for LLM Observability (OpenAI SDK)
patch(flask=True, requests=True, logging=True, openai=True)

# Service name for APM
config.flask["service_name"] = os.getenv("DD_SERVICE", "datadog-app-chat")

# Log format with Datadog correlation fields
FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s] '
    '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
    'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
    '- %(message)s'
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger("chat")
log.setLevel(logging.INFO)

# Optional: DogStatsD metrics (no-op fallback if agent isn’t present)
try:
    from datadog import statsd
except Exception:  # pragma: no cover
    class _NoopStatsd:
        def increment(self, *a, **k): pass
        def timing(self, *a, **k): pass
        def gauge(self, *a, **k): pass
    statsd = _NoopStatsd()

# --- App / client ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# NEVER put your key in the frontend
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Allowed models (optional, set with ALLOWED_MODELS env)
ALLOWED_MODELS = [m.strip() for m in os.getenv("ALLOWED_MODELS", "gpt-4o-mini,gpt-4o").split(",") if m.strip()]
DEFAULT_MODEL = ALLOWED_MODELS[0] if ALLOWED_MODELS else "gpt-4o-mini"
STRICT_MODEL_ENFORCEMENT = os.getenv("STRICT_MODEL_ENFORCEMENT", "true").lower() == "true"

@app.route("/api/models", methods=["GET"])
def list_models():
    return jsonify({"allowed": ALLOWED_MODELS, "default": DEFAULT_MODEL}), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"ok": True}), 200

def _trace_llm_call(name: str, model: str, prompt_chars: int):
    """
    Helper to start a manual span around the OpenAI SDK call.
    This complements ddtrace’s OpenAI integration and lets us add consistent LLM tags.
    """
    service = os.getenv("DD_SERVICE", "datadog-app-chat")
    span = tracer.trace(name, service=service, resource=model)
    # Standard LLM tags (don’t add raw prompts here)
    span.set_tag("llm.vendor", "openai")
    span.set_tag("llm.request.model", model)
    span.set_tag("llm.request.type", "responses")
    span.set_metric("llm.prompt.length_chars", float(prompt_chars))
    return span

# ---- Non-streaming (simple JSON) ----
@app.route("/api/chat", methods=["POST"])
def chat_once():
    t0 = time.time()
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages") or []
    system = payload.get("system") or "You are a helpful assistant."
    requested_model = (payload.get("model") or DEFAULT_MODEL).strip()
    model = requested_model

    # Enforce allow-list (no secret leakage in logs)
    if model not in ALLOWED_MODELS:
        log.warning("model_not_allowed", extra={"requested_model": model, "allowed": ALLOWED_MODELS})
        if STRICT_MODEL_ENFORCEMENT:
            return jsonify({"error": "model_not_allowed", "allowed": ALLOWED_MODELS, "default": DEFAULT_MODEL}), 400
        model = DEFAULT_MODEL

    prompt_chars = sum(len(m.get("content", "")) for m in messages)

    try:
        with _trace_llm_call("openai.responses.create", model, prompt_chars) as span:
            resp = client.responses.create(
                model=model,
                instructions=system,
                input=messages_to_responses_input(messages),
            )
            text = resp.output_text or ""
            # Response tags
            span.set_tag("llm.response.id", getattr(resp, "id", None))
            span.set_metric("llm.response.length_chars", float(len(text)))

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

    except Exception:
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
    requested_model = (payload.get("model") or DEFAULT_MODEL).strip()
    model = requested_model

    if model not in ALLOWED_MODELS:
        log.warning("model_not_allowed_stream", extra={"requested_model": model, "allowed": ALLOWED_MODELS})
        if STRICT_MODEL_ENFORCEMENT:
            def err():
                yield "event: error\ndata: model_not_allowed\n\n"
            return Response(err(), headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            })
        model = DEFAULT_MODEL

    prompt_chars = sum(len(m.get("content", "")) for m in messages)

    def sse():
        output_len = 0
        # Wrap the whole streaming exchange in a span
        with _trace_llm_call("openai.responses.stream", model, prompt_chars) as span:
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
                # Response tags at end
                span.set_metric("llm.response.length_chars", float(output_len))
            except Exception:
                log.exception("chat_stream failed during SSE")
                span.set_tag("error", True)
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
    """Flatten the messages for the Responses API. (We do not log raw content.)"""
    stitched = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        stitched.append(f"{role.upper()}: {content}")
    stitched.append("ASSISTANT:")
    return "\n".join(stitched)

if __name__ == "__main__":
    # Expect env:
    #  - OPENAI_API_KEY
    #  - DD_SERVICE, DD_ENV, DD_VERSION (k8s)
    #  - DD_TRACE_AGENT_URL or DD_AGENT_HOST for APM
    #  - (optional) DD_PROFILING_ENABLED=true (when running under ddtrace-run)
    app.run(host="0.0.0.0", port=5050, debug=True)
