FROM python:3.12.7-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py ./uid/

# Set up Datadog build arguments
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Expose the port
EXPOSE 5000

# Run the application with Datadog tracing and IAST enabled
CMD ["sh", "-c", "DD_IAST_ENABLED=true ddtrace-run python uid/app.py"]
