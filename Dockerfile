# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define build arguments
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA

# Define environment variables for Datadog
ENV DD_SERVICE=datadog-app
ENV DD_ENV=production
ENV DD_AGENT_HOST=datadog-agent
ENV DD_TRACE_ENABLED=true
ENV DD_VERSION=1.2.1
ENV DD_SERVICE=datadog-app
ENV DD_LOGS_INJECTION=true
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Run app.py when the container launches
# CMD ["python", "app.py"]
CMD ["ddtrace-run", "python", "-m", "app.py"]

