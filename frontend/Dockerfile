FROM nginx:alpine

# Copy the main nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the server block configuration
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy your application files if needed
COPY . /usr/share/nginx/html

EXPOSE 80