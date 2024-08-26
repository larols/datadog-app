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

# Define environment variables for Datadog
ENV DD_SERVICE=datadog-app
ENV DD_AGENT_HOST=datadog-agent
ENV DD_TRACE_ENABLED=true
ENV DD_VERSION=1.0
ENV DD_SERVICE=datadog-app

# Run app.py when the container launches
CMD ["python", "app.py"]

