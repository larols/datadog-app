FROM python:3.12.7-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (expects backend/chat/app_chat.py in repo root)
# Adjust the source path if your file is named differently.
COPY app_chat.py ./chat/

# Datadog build args -> env (for commit/repo attribution)
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Expose the chat service port (5050 in the sample app_chat.py)
EXPOSE 5050

# Run with Datadog tracing + IAST
CMD ["sh", "-c", "DD_IAST_ENABLED=true ddtrace-run python chat/app_chat.py"]
