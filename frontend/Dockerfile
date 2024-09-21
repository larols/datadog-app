# Stage 1: Build the React app
FROM node:14 as build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./

# Copy the rest of the application code
COPY public ./public
COPY src ./src

# List files to check if the correct files are present
RUN ls -la /app

# Install dependencies
RUN npm install

# Print npm logs regardless of the previous command's success
RUN cat /root/.npm/_logs/2024*.log || true

# Build the React app
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:alpine

# Copy the build output to Nginx's html folder
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]