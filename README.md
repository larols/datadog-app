# Project Name: Datadog App
This project consists of a frontend and backend application monitored by Datadog. The structure is organized into multiple directories for clarity. Please note that this setup was built for testing purposes in my private lab.

## Directory Structure
```
├── README.md
├── backend
│   ├── service-b
│   └── views
│       ├── Dockerfile             # Dockerfile for the views backend service
│       ├── app.py                 # Main application code for the views service
│       └── requirements.txt       # Python dependencies for the views service
├── frontend
│   ├── Dockerfile                 # Dockerfile for building the frontend React application
│   ├── package.json               # npm package configuration for frontend dependencies
│   ├── public
│   │   ├── favicon.ico            # Favicon for the web application
│   │   └── index.html             # Main HTML file for the React application
│   └── src
│       ├── app.css                # CSS styles for the React application
│       ├── app.js                 # Main JavaScript file for the React application
│       ├── index.css              # Additional CSS styles for the React application
│       └── index.js               # Entry point for the React application
└── k8s
    ├── frontend-deployment.yaml   # Kubernetes deployment configuration for the frontend
    ├── frontend-service.yaml      # Kubernetes service configuration for the frontend
    ├── nginx-config.yaml          # Nginx configuration for serving the frontend
    ├── nginx-deployment.yaml      # Kubernetes deployment configuration for Nginx
    ├── nginx-service.yaml         # Kubernetes service configuration for Nginx
    ├── views-deployment.yaml      # Kubernetes deployment configuration for the views backend
    └── views-service.yaml         # Kubernetes service configuration for the views backend
```

## Description of Files

### README.md
- This file provides an overview of the project, including its structure and purpose.

### Backend
- **service-b/**: Placeholder for another backend service if needed in the future.
- **views/**:
  - **Dockerfile**: Contains the instructions to build a Docker image for the views backend service.
  - **app.py**: The main application code that handles API requests and serves data.
  - **requirements.txt**: Lists the Python dependencies required for the views service.

### Frontend
- **Dockerfile**: Builds a Docker image for the React frontend application.
- **package.json**: Manages the dependencies and scripts for the frontend application.
- **public/**:
  - **favicon.ico**: The favicon displayed in the browser tab.
  - **index.html**: The main HTML template that is served to the user.
- **src/**:
  - **app.css**: Styles specifically for the app component.
  - **app.js**: Main React component that fetches data and renders the UI.
  - **index.css**: Global styles for the React application.
  - **index.js**: Entry point for the React application, rendering the app to the DOM.

### Kubernetes Configurations (k8s)
- **frontend-deployment.yaml**: Defines the deployment strategy for the frontend application in Kubernetes.
- **frontend-service.yaml**: Exposes the frontend application as a service in the Kubernetes cluster.
- **nginx-config.yaml**: Contains the Nginx configuration for serving the frontend application.
- **nginx-deployment.yaml**: Defines the deployment for the Nginx service.
- **nginx-service.yaml**: Exposes the Nginx service to handle incoming traffic.
- **views-deployment.yaml**: Defines the deployment for the views backend service.
- **views-service.yaml**: Exposes the views backend service in the Kubernetes cluster.

This setup was built for testing purposes in my private lab.
