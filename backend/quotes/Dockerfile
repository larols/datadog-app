# Use the official Python image as the base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the directory for the app
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables for Datadog instrumentation
ENV DD_SERVICE="datadog-app-quotes"
ENV DD_ENV="production"
ENV DD_VERSION="${VERSION}"

# Run the application
CMD ["python", "app.py"]
