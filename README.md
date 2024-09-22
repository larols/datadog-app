# Project Name: Datadog App
This project consists of a frontend and backend application monitored by Datadog. The structure is organized into multiple directories for clarity. Please note that this setup was built for testing purposes in my private lab.

## Directory Structure
```
├── README.md
├── backend
│   ├── uid
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   └── views
│       ├── Dockerfile
│       ├── app.py
│       └── requirements.txt
├── frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── public
│   │   ├── favicon.ico
│   │   └── index.html
│   └── src
│       ├── app.css
│       ├── app.js
│       ├── index.css
│       └── index.js
├── k8s
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── nginx-config.yaml
│   ├── nginx-deployment.yaml
│   ├── nginx-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── uid-deployment.yaml
│   ├── uid-service.yaml
│   ├── views-deployment.yaml
│   └── views-service.yaml
└── static-analysis.datadog.yml
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
