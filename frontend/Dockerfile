FROM nginx:alpine

# Copy your Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy other necessary files
COPY . /usr/share/nginx/html

EXPOSE 80