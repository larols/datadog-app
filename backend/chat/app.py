# app_chat.py
import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # tweak for your domains in prod

# NEVER put your key in the frontend
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---- Non-streaming (simple JSON) ----
@app.route("/api/chat", methods=["POST"])
def chat_once():
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages") or []
    system = payload.get("system") or "You are a helpful assistant."
    model = payload.get("model") or "gpt-4o"

    # Make a single-response call (no streaming)
    resp = client.responses.create(
        model=model,
        instructions=system,
        input=messages_to_responses_input(messages),
    )
    return jsonify({"text": resp.output_text, "response_id": resp.id})

# ---- Streaming via SSE ----
@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages") or []
    system = payload.get("system") or "You are a helpful assistant."
    model = payload.get("model") or "gpt-4o"

    def sse():
        stream = client.responses.stream(
            model=model,
            instructions=system,
            input=messages_to_responses_input(messages),
        )
        # stream is a context manager that yields events
        with stream as events:
            for event in events:
                # event.type is things like "response.output_text.delta", "response.completed", etc.
                if hasattr(event, "delta") and isinstance(event.delta, str) and event.delta:
                    yield f"data: {event.delta}\n\n"
            # tell the EventSource the stream is complete
            yield "event: done\ndata: [DONE]\n\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # disable buffering on nginx if used
    }
    return Response(sse(), headers=headers)

def messages_to_responses_input(messages):
    """
    Your React will send an array like:
    [{role:'user', content:'hi'}, {role:'assistant', content:'hello'}]
    The Responses API accepts plain text, lists of parts, or prior turn context.
    We’ll just flatten to a single text prompt with simple role tags,
    which works well for many apps. For richer formatting, send a list of
    input parts per the docs.
    """
    stitched = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        stitched.append(f"{role.upper()}: {content}")
    stitched.append("ASSISTANT:")
    return "\n".join(stitched)

if __name__ == "__main__":
    # export OPENAI_API_KEY=sk-...
    app.run(host="0.0.0.0", port=5050, debug=True)
