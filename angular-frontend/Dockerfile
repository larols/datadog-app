FROM node:18-alpine as build 
WORKDIR /app
COPY package*.json ./ 
RUN npm install
COPY . /app
RUN npm run build -- --prod  

FROM nginx:alpine
COPY --from=build /app/dist/angular-frontend /usr/share/nginx/html

ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]