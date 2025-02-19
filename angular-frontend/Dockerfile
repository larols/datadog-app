# Stage 1: Build the Angular app
FROM node:18-alpine as build 
WORKDIR /app
COPY package*.json ./ 
RUN npm install
COPY..
RUN npm run build -- --prod  

# Stage 2: Serve the app with Nginx
FROM nginx:alpine
COPY --from=build /app/dist/angular-frontend /usr/share/nginx/html

# Add your Datadog environment variables here if needed
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]