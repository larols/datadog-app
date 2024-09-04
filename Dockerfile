# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define build arguments
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ARG VERSION_FILE_CONTENT

# Define environment variables for Datadog
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Create version.json from the VERSION_FILE_CONTENT build argument
RUN echo $VERSION_FILE_CONTENT > /app/version.json

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
# CMD ["python", "app.py"]
CMD ["ddtrace-run", "python", "-m", "app"]
